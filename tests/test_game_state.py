"""Unit tests ของโดเมนปลาและสถานะการเล่น (Sprint 2)"""

import pytest

from src.fish import FRESHWATER, MARINE, Fish
import time

from src.game_state import (START_MONEY, FishNotFoundError,
                            FishProtectedError, GameState,
                            NotEnoughMoneyError)


class FixedRandom:
    """ตัวสุ่มปลอมที่คืนค่าเดิมเสมอ ทำให้ทดสอบผลลัพธ์แบบตายตัวได้"""

    def __init__(self, value):
        self.value = value

    def uniform(self, low, high):
        return self.value


def make_fish(name="Catfish", location=FRESHWATER, weight=2.0, price=30):
    return Fish(name, location, weight, price)


class TestFishCalculation:
    def test_weight_scales_with_bait_level(self):
        rng = FixedRandom(2.0)
        assert Fish.roll_weight(1, rng=rng) == 3.0
        assert Fish.roll_weight(3, rng=rng) == 5.0

    def test_price_is_weight_times_rate_and_bait(self):
        assert Fish.price_for(2.0, 1) == 30
        assert Fish.price_for(2.0, 3) == 90

    def test_catch_builds_complete_fish(self):
        fish = Fish.catch("Tuna", MARINE, 2, rng=FixedRandom(1.0))
        assert fish.name == "Tuna"
        assert fish.location == MARINE
        assert fish.weight_kg == 2.0
        assert fish.price == 60

    def test_round_trip_through_dict(self):
        fish = make_fish()
        assert Fish.from_dict(fish.to_dict()).to_dict() == fish.to_dict()

    def test_from_dict_uses_defaults_for_missing_fields(self):
        restored = Fish.from_dict({})
        assert restored.name == "ปลาปริศนา"
        assert restored.price == 0


class TestMoney:
    def test_starts_with_default_money(self):
        assert GameState().money == START_MONEY

    def test_sell_all_adds_money_and_clears_bag(self):
        state = GameState(money=0, inventory=[make_fish(price=30), make_fish(price=20)])
        assert state.sell_all() == 50
        assert state.money == 50
        assert state.inventory == []

    def test_sell_empty_bag_gives_nothing(self):
        state = GameState(money=10)
        assert state.sell_all() == 0
        assert state.money == 10


class TestUpgrade:
    def test_bait_cost_grows_with_level(self):
        assert GameState(bait_level=1).bait_cost == 50
        assert GameState(bait_level=3).bait_cost == 150

    def test_upgrade_deducts_money_and_raises_level(self):
        state = GameState(money=100, bait_level=1)
        assert state.upgrade_bait() == 2
        assert state.money == 50

    def test_upgrade_rod_deducts_money(self):
        state = GameState(money=60, rod_level=1)
        assert state.upgrade_rod() == 2
        assert state.money == 10

    def test_rejects_upgrade_when_money_is_short(self):
        state = GameState(money=10, bait_level=1)
        with pytest.raises(NotEnoughMoneyError):
            state.upgrade_bait()
        assert state.money == 10
        assert state.bait_level == 1


class TestSearchFilterSort:
    @pytest.fixture
    def state(self):
        return GameState(inventory=[
            make_fish("Catfish", FRESHWATER, 1.0, 10),
            make_fish("Yellowfin Tuna", MARINE, 5.0, 90),
            make_fish("Nile Tilapia", FRESHWATER, 3.0, 40),
        ])

    def test_search_is_case_insensitive_and_partial(self, state):
        assert [f.name for f in state.search_inventory("tuna")] == ["Yellowfin Tuna"]
        assert len(state.search_inventory("i")) == 3

    def test_search_returns_empty_when_no_match(self, state):
        assert state.search_inventory("shark") == []

    def test_filter_by_location(self, state):
        assert len(state.filter_inventory(FRESHWATER)) == 2
        assert len(state.filter_inventory(MARINE)) == 1

    def test_sort_by_price_descending(self, state):
        assert [f.price for f in state.sort_inventory("price")] == [90, 40, 10]

    def test_sort_by_weight_ascending(self, state):
        ordered = state.sort_inventory("weight", descending=False)
        assert [f.weight_kg for f in ordered] == [1.0, 3.0, 5.0]

    def test_sort_by_name(self, state):
        assert state.sort_inventory("name", descending=False)[0].name == "Catfish"

    def test_sort_rejects_unknown_key(self, state):
        with pytest.raises(ValueError):
            state.sort_inventory("color")

    def test_sort_does_not_mutate_inventory(self, state):
        original = [f.name for f in state.inventory]
        state.sort_inventory("price")
        assert [f.name for f in state.inventory] == original


class TestSummary:
    def test_empty_bag_summary(self):
        assert GameState().summary() == {
            "count": 0, "total_price": 0, "average_weight": 0.0, "heaviest": None,
        }

    def test_summary_counts_and_averages(self):
        state = GameState(inventory=[
            make_fish("A", FRESHWATER, 1.0, 10),
            make_fish("B", MARINE, 4.0, 30),
        ])
        summary = state.summary()
        assert summary["count"] == 2
        assert summary["total_price"] == 40
        assert summary["average_weight"] == 2.5
        assert summary["heaviest"].name == "B"


class TestSerialization:
    def test_round_trip_keeps_everything(self):
        state = GameState(money=250, inventory=[make_fish()], bait_level=2, rod_level=3)
        assert GameState.from_dict(state.to_dict()).to_dict() == state.to_dict()

    def test_from_dict_uses_defaults(self):
        state = GameState.from_dict({})
        assert state.money == START_MONEY
        assert state.inventory == []
        assert state.bait_level == 1


class TestSellOne:
    """ขายปลาทีละตัว"""

    def test_returns_the_price_of_that_fish(self):
        state = GameState(money=0, inventory=[make_fish(price=40),
                                              make_fish(price=70)])
        assert state.sell_fish(state.inventory[0]) == 40

    def test_adds_the_money(self):
        state = GameState(money=10, inventory=[make_fish(price=40)])
        state.sell_fish(state.inventory[0])
        assert state.money == 50

    def test_removes_only_that_fish(self):
        state = GameState(inventory=[make_fish(price=40), make_fish(price=70)])
        keep = state.inventory[1]
        state.sell_fish(state.inventory[0])
        assert state.inventory == [keep]

    def test_identical_fish_are_told_apart(self):
        """ปลาชื่อและราคาเหมือนกันสองตัว ขายไปตัวเดียวต้องเหลืออีกตัว"""
        first, second = make_fish(), make_fish()
        state = GameState(inventory=[first, second])
        state.sell_fish(first)
        assert state.inventory == [second]

    def test_selling_a_fish_that_is_not_in_the_bag(self):
        state = GameState(inventory=[make_fish()])
        with pytest.raises(ValueError):
            state.sell_fish(make_fish())

    def test_selling_from_an_empty_bag(self):
        with pytest.raises(ValueError):
            GameState().sell_fish(make_fish())


class TestSellSpecies:
    """ขายปลายกชนิด"""

    def bag(self):
        return GameState(money=0, inventory=[
            make_fish("Carp", price=40),
            make_fish("Tuna", price=90),
            make_fish("Carp", price=60),
        ])

    def test_counts_how_many_of_a_species(self):
        assert self.bag().count_species("Carp") == 2

    def test_counts_zero_for_a_species_not_in_the_bag(self):
        assert self.bag().count_species("Shark") == 0

    def test_returns_count_and_total(self):
        assert self.bag().sell_species("Carp") == (2, 100)

    def test_removes_every_fish_of_that_species(self):
        state = self.bag()
        state.sell_species("Carp")
        assert [fish.name for fish in state.inventory] == ["Tuna"]

    def test_keeps_other_species_untouched(self):
        state = self.bag()
        state.sell_species("Carp")
        assert state.inventory[0].price == 90

    def test_adds_the_total_to_the_money(self):
        state = self.bag()
        state.sell_species("Carp")
        assert state.money == 100

    def test_selling_a_species_that_is_not_in_the_bag(self):
        with pytest.raises(ValueError):
            self.bag().sell_species("Shark")

    def test_selling_everything_one_species_at_a_time(self):
        """ขายยกชนิดจนหมดต้องได้เงินเท่ากับขายทั้งกระเป๋ารวดเดียว"""
        state = self.bag()
        state.sell_species("Carp")
        state.sell_species("Tuna")
        assert state.money == 190
        assert state.inventory == []


class TestUpdateFish:
    """แก้ไขข้อมูลปลา — ส่วน U ของ CRUD"""

    def bag(self):
        return GameState(money=0, inventory=[
            make_fish("Carp", price=40), make_fish("Tuna", price=90)])

    def test_rename_changes_the_name(self):
        state = self.bag()
        assert state.rename_fish(state.inventory[0], "เจ้าอ้วน") == "เจ้าอ้วน"
        assert state.inventory[0].name == "เจ้าอ้วน"

    def test_rename_trims_spaces(self):
        state = self.bag()
        assert state.rename_fish(state.inventory[0], "  เจ้าอ้วน  ") == "เจ้าอ้วน"

    def test_rename_rejects_blank_name(self):
        state = self.bag()
        with pytest.raises(ValueError):
            state.rename_fish(state.inventory[0], "   ")

    def test_rename_does_not_touch_other_fish(self):
        state = self.bag()
        state.rename_fish(state.inventory[0], "เจ้าอ้วน")
        assert state.inventory[1].name == "Tuna"

    def test_rename_a_fish_that_is_not_in_the_bag(self):
        with pytest.raises(FishNotFoundError):
            self.bag().rename_fish(make_fish(), "เจ้าอ้วน")

    def test_set_keep_marks_the_fish(self):
        state = self.bag()
        assert state.set_keep(state.inventory[0], True) is True
        assert state.inventory[0].keep is True

    def test_toggle_keep_flips_the_flag(self):
        state = self.bag()
        fish = state.inventory[0]
        assert state.toggle_keep(fish) is True
        assert state.toggle_keep(fish) is False

    def test_kept_fish_lists_only_marked_ones(self):
        state = self.bag()
        state.toggle_keep(state.inventory[1])
        assert [f.name for f in state.kept_fish()] == ["Tuna"]

    def test_keeping_a_fish_that_is_not_in_the_bag(self):
        with pytest.raises(FishNotFoundError):
            self.bag().set_keep(make_fish(), True)


class TestKeepProtectsFromSelling:
    """ปลาที่ทำเครื่องหมายเก็บไว้ต้องไม่ถูกขายไม่ว่าทางไหน"""

    def bag(self):
        state = GameState(money=0, inventory=[
            make_fish("Carp", price=40), make_fish("Tuna", price=90),
            make_fish("Carp", price=60)])
        state.toggle_keep(state.inventory[1])
        return state

    def test_sell_fish_refuses_a_kept_fish(self):
        state = self.bag()
        with pytest.raises(FishProtectedError):
            state.sell_fish(state.inventory[1])
        assert state.money == 0

    def test_sell_all_skips_kept_fish(self):
        state = self.bag()
        assert state.sell_all() == 100
        assert [f.name for f in state.inventory] == ["Tuna"]

    def test_sell_species_skips_kept_fish(self):
        state = GameState(money=0, inventory=[
            make_fish("Carp", price=40), make_fish("Carp", price=60)])
        state.toggle_keep(state.inventory[0])
        assert state.sell_species("Carp") == (1, 60)
        assert len(state.inventory) == 1

    def test_unkeeping_lets_it_be_sold_again(self):
        state = self.bag()
        kept = state.inventory[1]
        state.toggle_keep(kept)
        assert state.sell_fish(kept) == 90


class TestCustomExceptions:
    """ข้อกำหนดของสปรินต์: ลบรายการที่ไม่มีในระบบต้องโยน Custom Exception"""

    def test_selling_a_missing_fish_raises_the_custom_error(self):
        with pytest.raises(FishNotFoundError):
            GameState().sell_fish(make_fish())

    def test_selling_a_missing_species_raises_the_custom_error(self):
        with pytest.raises(FishNotFoundError):
            GameState().sell_species("Shark")

    def test_custom_errors_are_still_value_errors(self):
        """สืบทอดจาก ValueError โค้ดเดิมที่ดัก ValueError จึงยังทำงานได้"""
        assert issubclass(FishNotFoundError, ValueError)
        assert issubclass(FishProtectedError, ValueError)

    def test_error_message_names_the_fish(self):
        try:
            GameState().sell_fish(make_fish("Carp"))
        except FishNotFoundError as error:
            assert "Carp" in str(error)


class TestPerformanceOnLargeData:
    """ประสิทธิภาพของอัลกอริทึมกับชุดข้อมูลขนาดใหญ่ (TC-P01 ถึง TC-P03)"""

    def big_bag(self, size=1000):
        import random
        rng = random.Random(42)
        names = ["Carp", "Tuna", "Salmon", "Mullet", "Perch", "Herring"]
        fish = [Fish(rng.choice(names), rng.choice([FRESHWATER, MARINE]),
                     round(rng.uniform(0.5, 9.9), 2), rng.randint(10, 300))
                for _ in range(size)]
        return GameState(inventory=fish)

    def test_sorting_1000_items_is_fast(self):
        state = self.big_bag()
        start = time.perf_counter()
        ordered = state.sort_inventory("weight")
        elapsed = (time.perf_counter() - start) * 1000
        assert len(ordered) == 1000
        assert elapsed < 50, f"เรียง 1000 รายการใช้ {elapsed:.1f} ms เกิน 50 ms"

    def test_sorting_keeps_every_item(self):
        state = self.big_bag()
        for key in ("name", "weight", "price"):
            assert len(state.sort_inventory(key)) == 1000

    def test_searching_1000_items_is_fast(self):
        state = self.big_bag()
        start = time.perf_counter()
        found = state.search_inventory("carp")
        elapsed = (time.perf_counter() - start) * 1000
        assert found and all("carp" in f.name.lower() for f in found)
        assert elapsed < 50, f"ค้นหา 1000 รายการใช้ {elapsed:.1f} ms เกิน 50 ms"

    def test_summary_on_1000_items_is_fast(self):
        state = self.big_bag()
        start = time.perf_counter()
        stats = state.summary()
        elapsed = (time.perf_counter() - start) * 1000
        assert stats["count"] == 1000
        assert elapsed < 50, f"สรุปสถิติใช้ {elapsed:.1f} ms เกิน 50 ms"

    def test_sorting_is_stable_across_runs(self):
        """เรียงชุดเดิมสองครั้งต้องได้ลำดับเดิมเป๊ะ"""
        state = self.big_bag()
        first = [f.price for f in state.sort_inventory("price")]
        second = [f.price for f in state.sort_inventory("price")]
        assert first == second
