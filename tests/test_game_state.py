"""Unit tests ของโดเมนปลาและสถานะการเล่น (Sprint 2)"""

import pytest

from src.fish import FRESHWATER, MARINE, Fish
from src.game_state import START_MONEY, GameState, NotEnoughMoneyError


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
