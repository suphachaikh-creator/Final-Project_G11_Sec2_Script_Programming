"""Unit tests ของตรรกะหน้าจอ GUI (Sprint 3)

**ไม่มีเทสต์ใดในไฟล์นี้สร้าง `tk.Tk()`** และไม่มีการ import tkinter เลย
เพราะเครื่องที่รัน CI ไม่มีหน้าจอ ถ้าเปิดหน้าต่างจริงจะพังทันที
ทุกอย่างที่ทดสอบอยู่ใน `src/gui/presenter.py` ซึ่งเป็นตรรกะล้วน
"""

import pytest

from src.fish import BRACKISH, FRESHWATER, MARINE, Fish
from src.game_state import GameState
from src.gui.presenter import (ALL_LOCATIONS, DashboardPresenter,
                               FishingPresenter, InventoryPresenter,
                               ShopPresenter, TkClock, location_label)


def make_state(money=100, fish=None, bait_level=1, rod_level=1):
    return GameState(money=money, inventory=fish or [],
                     bait_level=bait_level, rod_level=rod_level)


def sample_fish():
    return [
        Fish("Goldfish", FRESHWATER, 1.5, 30),
        Fish("Atlantic salmon", MARINE, 4.0, 90),
        Fish("Mullet", BRACKISH, 2.5, 60),
    ]


class FakeApi:
    def __init__(self, name="Goldfish", using_fallback=False):
        self.name = name
        self.using_fallback = using_fallback

    def random_species(self, location, rng=None):
        return {"name": self.name, "location": location}


class FakeRng:
    """ตัวสุ่มปลอม ให้ผลเดิมทุกครั้ง เทสต์จึงตรวจค่าที่แน่นอนได้"""

    def __init__(self, length=2, letter="a", weight=2.0):
        self.length = length
        self.letter = letter
        self.weight = weight

    def randint(self, low, high):
        return self.length

    def choice(self, options):
        return self.letter

    def uniform(self, low, high):
        return self.weight


class TestTkClock:
    """นาฬิกาที่เดินตามจังหวะ root.after() แทนเวลาจริง"""

    def test_starts_at_zero(self):
        assert TkClock(100)() == 0.0

    def test_tick_advances_by_interval(self):
        clock = TkClock(100)
        clock.tick()
        clock.tick()
        assert clock() == pytest.approx(0.2)

    def test_can_be_used_as_a_clock_function(self):
        """ต้องเรียกใช้แทนฟังก์ชันนาฬิกาได้โดยตรง"""
        clock = TkClock(500)
        clock.tick()
        assert clock() == pytest.approx(0.5)


class TestInventorySorting:
    def test_click_new_column_sorts_descending(self):
        presenter = InventoryPresenter(make_state(fish=sample_fish()))
        assert presenter.toggle_sort("weight") == ("weight", True)

    def test_click_same_column_reverses_direction(self):
        """คลิกหัวคอลัมน์เดิมซ้ำต้องสลับทิศ ขึ้นแล้วลงได้"""
        presenter = InventoryPresenter(make_state(fish=sample_fish()))
        presenter.toggle_sort("weight")
        assert presenter.toggle_sort("weight") == ("weight", False)

    def test_rejects_column_that_cannot_be_sorted(self):
        presenter = InventoryPresenter(make_state(fish=sample_fish()))
        with pytest.raises(ValueError):
            presenter.toggle_sort("location")

    def test_sorts_rows_by_weight_descending(self):
        presenter = InventoryPresenter(make_state(fish=sample_fish()))
        presenter.toggle_sort("weight")
        assert [row[0] for row in presenter.visible_rows()] == [
            "Atlantic salmon", "Mullet", "Goldfish"]

    def test_sorts_rows_by_weight_ascending(self):
        presenter = InventoryPresenter(make_state(fish=sample_fish()))
        presenter.toggle_sort("weight")
        presenter.toggle_sort("weight")
        assert [row[0] for row in presenter.visible_rows()] == [
            "Goldfish", "Mullet", "Atlantic salmon"]

    def test_heading_shows_arrow_for_active_column(self):
        presenter = InventoryPresenter(make_state(fish=sample_fish()))
        presenter.toggle_sort("name")
        assert "▼" in presenter.heading_text("name")
        presenter.toggle_sort("name")
        assert "▲" in presenter.heading_text("name")

    def test_heading_has_no_arrow_for_other_columns(self):
        presenter = InventoryPresenter(make_state(fish=sample_fish()))
        assert presenter.heading_text("location") == "แหล่งน้ำ"

    def test_sorting_does_not_mutate_inventory(self):
        """เรียงเพื่อดูผลต้องไม่เปลี่ยนลำดับจริงในกระเป๋า"""
        state = make_state(fish=sample_fish())
        before = list(state.inventory)
        presenter = InventoryPresenter(state)
        presenter.toggle_sort("name")
        presenter.visible_rows()
        assert state.inventory == before


class TestInventorySearchAndFilter:
    def test_search_narrows_rows(self):
        presenter = InventoryPresenter(make_state(fish=sample_fish()))
        presenter.keyword = "salmon"
        assert [row[0] for row in presenter.visible_rows()] == ["Atlantic salmon"]

    def test_search_ignores_case(self):
        presenter = InventoryPresenter(make_state(fish=sample_fish()))
        presenter.keyword = "GOLD"
        assert len(presenter.visible_rows()) == 1

    def test_blank_search_shows_everything(self):
        presenter = InventoryPresenter(make_state(fish=sample_fish()))
        presenter.keyword = "   "
        assert len(presenter.visible_rows()) == 3

    @pytest.mark.parametrize("location,expected", [
        (FRESHWATER, 1), (MARINE, 1), (BRACKISH, 1), (ALL_LOCATIONS, 3)])
    def test_filter_by_location(self, location, expected):
        presenter = InventoryPresenter(make_state(fish=sample_fish()))
        presenter.location_filter = location
        assert len(presenter.visible_rows()) == expected

    def test_search_and_filter_work_together(self):
        presenter = InventoryPresenter(make_state(fish=sample_fish()))
        presenter.keyword = "salmon"
        presenter.location_filter = FRESHWATER
        assert presenter.visible_rows() == []

    def test_rows_are_all_text_ready_for_the_table(self):
        presenter = InventoryPresenter(make_state(fish=sample_fish()))
        row = presenter.visible_rows()[0]
        assert len(row) == 4
        assert all(isinstance(cell, str) for cell in row)


class TestInventorySummary:
    def test_message_when_bag_is_empty(self):
        presenter = InventoryPresenter(make_state())
        assert presenter.summary_lines() == ["ยังไม่มีปลาในกระเป๋า"]

    def test_summary_uses_game_state_not_an_api(self):
        presenter = InventoryPresenter(make_state(fish=sample_fish()))
        lines = presenter.summary_lines()
        assert "จำนวนปลา 3 ตัว" in lines[0]
        assert "$180" in lines[1]

    def test_sell_all_reports_amount(self):
        state = make_state(fish=sample_fish())
        presenter = InventoryPresenter(state)
        assert presenter.sell_all() == "ขายปลาได้ $180"
        assert state.inventory == []

    def test_sell_all_on_empty_bag(self):
        presenter = InventoryPresenter(make_state())
        assert presenter.sell_all() == "ยังไม่มีปลาให้ขาย"


class TestShopButtons:
    def test_buttons_enabled_when_player_can_afford(self):
        presenter = ShopPresenter(make_state(money=500))
        assert all(item["enabled"] for item in presenter.items())

    def test_buttons_disabled_when_money_runs_out(self):
        """เงินไม่พอ ปุ่มซื้อต้องถูกปิดเอง"""
        presenter = ShopPresenter(make_state(money=10))
        assert not any(item["enabled"] for item in presenter.items())

    def test_button_disables_itself_after_buying(self):
        state = make_state(money=60)
        presenter = ShopPresenter(state)
        presenter.buy("bait")
        assert not presenter.items()[0]["enabled"]

    def test_buying_raises_the_level(self):
        state = make_state(money=500)
        ok, message = ShopPresenter(state).buy("rod")
        assert ok is True
        assert state.rod_level == 2
        assert "เลเวล 2" in message

    def test_buying_without_money_returns_a_message_not_a_crash(self):
        ok, message = ShopPresenter(make_state(money=0)).buy("bait")
        assert ok is False
        assert "$50" in message

    def test_unknown_item(self):
        ok, message = ShopPresenter(make_state()).buy("boat")
        assert ok is False
        assert "boat" in message


class TestFishingRound:
    def make_presenter(self, rod_level=1):
        state = make_state(rod_level=rod_level)
        clock = TkClock(1000)
        presenter = FishingPresenter(state, FakeApi(), rng=FakeRng(), clock=clock)
        return presenter, clock, state

    def test_starting_a_round_creates_a_minigame(self):
        presenter, _, _ = self.make_presenter()
        presenter.start(MARINE)
        assert presenter.is_running is True
        assert presenter.location == MARINE

    def test_not_running_before_the_first_round(self):
        presenter, _, _ = self.make_presenter()
        assert presenter.is_running is False

    def test_target_text_hides_letters_already_typed(self):
        presenter, _, _ = self.make_presenter()
        presenter.start(FRESHWATER)
        presenter.press("a")
        assert presenter.target_text().startswith("·")

    def test_progress_ratio_falls_as_the_clock_ticks(self):
        presenter, clock, _ = self.make_presenter()
        presenter.start(FRESHWATER)
        before = presenter.progress_ratio()
        clock.tick()
        assert presenter.progress_ratio() < before

    def test_progress_ratio_never_goes_below_zero(self):
        presenter, clock, _ = self.make_presenter()
        presenter.start(FRESHWATER)
        for _ in range(50):
            clock.tick()
        assert presenter.progress_ratio() == 0.0

    def test_wrong_key_does_not_advance(self):
        presenter, _, _ = self.make_presenter()
        presenter.start(FRESHWATER)
        assert presenter.press("z") is False

    def test_keys_are_ignored_after_time_runs_out(self):
        """หมดเวลาแล้วกดปุ่มต้องไม่มีผล"""
        presenter, clock, _ = self.make_presenter()
        presenter.start(FRESHWATER)
        for _ in range(50):
            clock.tick()
        assert presenter.press("a") is False

    def test_finishing_a_won_round_adds_a_fish(self):
        presenter, _, state = self.make_presenter()
        presenter.start(FRESHWATER)
        presenter.press("a")
        presenter.press("a")
        result = presenter.finish()
        assert result["success"] is True
        assert len(state.inventory) == 1
        assert state.inventory[0].name == "Goldfish"

    def test_finishing_a_lost_round_adds_nothing(self):
        presenter, clock, state = self.make_presenter()
        presenter.start(FRESHWATER)
        for _ in range(50):
            clock.tick()
        result = presenter.finish()
        assert result["success"] is False
        assert state.inventory == []

    def test_result_text_for_a_win(self):
        presenter, _, _ = self.make_presenter()
        presenter.start(FRESHWATER)
        presenter.press("a")
        presenter.press("a")
        presenter.finish()
        assert "Goldfish" in presenter.result_text()

    def test_result_text_for_a_loss(self):
        presenter, clock, _ = self.make_presenter()
        presenter.start(FRESHWATER)
        for _ in range(50):
            clock.tick()
        presenter.finish()
        assert "ปลาหลุด" in presenter.result_text()

    def test_result_text_is_blank_before_any_round(self):
        presenter, _, _ = self.make_presenter()
        assert presenter.result_text() == ""

    def test_finish_without_a_round_returns_none(self):
        presenter, _, _ = self.make_presenter()
        assert presenter.finish() is None


class TestFishingDifficulty:
    """ตัวปรับความยากอัตโนมัติ (Final Sprint) ต่อเข้ากับรอบการตกปลา"""

    def make_presenter(self, rounds=None):
        from src.difficulty import DifficultyTuner
        state = make_state(rod_level=2)
        clock = TkClock(1000)
        tuner = DifficultyTuner(rounds or [])
        presenter = FishingPresenter(state, FakeApi(), rng=FakeRng(),
                                     clock=clock, tuner=tuner)
        return presenter, clock, tuner

    def test_round_result_is_recorded(self):
        presenter, clock, tuner = self.make_presenter()
        presenter.start(FRESHWATER)
        for _ in range(50):
            clock.tick()
        presenter.finish()
        assert len(tuner.rounds) == 1

    def test_history_is_put_into_the_game_state_for_autosave(self):
        presenter, clock, tuner = self.make_presenter()
        presenter.start(FRESHWATER)
        for _ in range(50):
            clock.tick()
        presenter.finish()
        assert presenter.state.difficulty_data == tuner.to_dict()

    def test_difficulty_is_applied_to_the_new_round(self):
        from src.difficulty import HARD
        rounds = [{"hits": 10, "total": 10} for _ in range(5)]
        presenter, _, tuner = self.make_presenter(rounds)
        presenter.start(FRESHWATER)
        assert presenter.last_settings["level"] == HARD
        assert presenter.minigame.time_limit == tuner.time_limit_for(2)

    def test_text_tells_the_player_the_current_level(self):
        rounds = [{"hits": 10, "total": 10} for _ in range(5)]
        presenter, _, _ = self.make_presenter(rounds)
        assert "ยากขึ้น" in presenter.difficulty_text()
        assert "100%" in presenter.difficulty_text()

    def test_text_is_blank_without_a_tuner(self):
        presenter = FishingPresenter(make_state(), FakeApi())
        assert presenter.difficulty_text() == ""

    def test_works_without_a_tuner_at_all(self):
        """ไม่มีตัวปรับความยากก็ต้องเล่นได้ตามปกติ"""
        presenter = FishingPresenter(make_state(), FakeApi(), rng=FakeRng(),
                                     clock=TkClock(1000))
        presenter.start(FRESHWATER)
        assert presenter.is_running is True
        assert presenter.last_settings is None


class TestDashboard:
    def test_status_lines_show_player_state(self):
        presenter = DashboardPresenter(make_state(money=250, fish=sample_fish()))
        lines = presenter.status_lines()
        assert "เงิน $250" in lines[0]
        assert "3 ตัว" in lines[3]

    def test_warns_the_player_when_using_local_data(self):
        presenter = DashboardPresenter(make_state(), FakeApi(using_fallback=True))
        assert "ออฟไลน์" in presenter.api_status()

    def test_says_online_when_the_api_works(self):
        presenter = DashboardPresenter(make_state(), FakeApi())
        assert "ออนไลน์" in presenter.api_status()

    def test_blank_when_there_is_no_api(self):
        assert DashboardPresenter(make_state()).api_status() == ""


class TestLabels:
    @pytest.mark.parametrize("code,expected", [
        (FRESHWATER, "ทะเลสาบน้ำจืด"),
        (MARINE, "ทะเลลึก"),
        (BRACKISH, "ปากแม่น้ำน้ำกร่อย")])
    def test_thai_labels(self, code, expected):
        assert location_label(code) == expected

    def test_unknown_code_falls_back_to_itself(self):
        assert location_label("lava") == "lava"


class TestSellFromTheTable:
    """ขายทีละตัวและขายยกชนิดจากแถวที่เลือกในตาราง"""

    def bag(self):
        return make_state(money=0, fish=[
            Fish("Carp", FRESHWATER, 1.0, 40),
            Fish("Tuna", MARINE, 4.0, 90),
            Fish("Carp", FRESHWATER, 2.0, 60),
        ])

    def test_row_index_maps_to_the_fish_shown(self):
        """ลำดับต้องตรงกับตารางเสมอ ไม่งั้นจะขายผิดตัว"""
        presenter = InventoryPresenter(self.bag())
        for index, row in enumerate(presenter.visible_rows()):
            assert presenter.fish_at(index).name == row[0]

    def test_row_index_follows_the_sort_order(self):
        presenter = InventoryPresenter(self.bag())
        presenter.toggle_sort("weight")
        assert presenter.fish_at(0).name == "Tuna"
        presenter.toggle_sort("weight")
        assert presenter.fish_at(0).name == "Carp"

    def test_row_index_follows_the_filter(self):
        presenter = InventoryPresenter(self.bag())
        presenter.location_filter = MARINE
        assert presenter.fish_at(0).name == "Tuna"
        assert presenter.fish_at(1) is None

    @pytest.mark.parametrize("index", [None, -1, 99])
    def test_no_fish_for_a_row_that_does_not_exist(self, index):
        assert InventoryPresenter(self.bag()).fish_at(index) is None

    def test_sell_one_removes_a_single_fish(self):
        state = self.bag()
        presenter = InventoryPresenter(state)
        target = presenter.fish_at(0)
        message = presenter.sell_one(0)
        assert target.name in message
        assert len(state.inventory) == 2

    def test_sell_one_pays_only_that_fish(self):
        state = self.bag()
        presenter = InventoryPresenter(state)
        price = presenter.fish_at(0).price
        presenter.sell_one(0)
        assert state.money == price

    def test_sell_one_without_a_selection(self):
        state = self.bag()
        assert InventoryPresenter(state).sell_one(None) == "ยังไม่ได้เลือกปลา"
        assert len(state.inventory) == 3

    def test_species_count_for_the_selected_row(self):
        presenter = InventoryPresenter(self.bag())
        index = next(i for i in range(3) if presenter.fish_at(i).name == "Carp")
        assert presenter.species_count_at(index) == 2

    def test_species_count_without_a_selection(self):
        assert InventoryPresenter(self.bag()).species_count_at(None) == 0

    def test_sell_species_removes_every_one_of_them(self):
        state = self.bag()
        presenter = InventoryPresenter(state)
        index = next(i for i in range(3) if presenter.fish_at(i).name == "Carp")
        message = presenter.sell_species_at(index)
        assert "2 ตัว" in message
        assert [fish.name for fish in state.inventory] == ["Tuna"]

    def test_sell_species_pays_the_total(self):
        state = self.bag()
        presenter = InventoryPresenter(state)
        index = next(i for i in range(3) if presenter.fish_at(i).name == "Carp")
        presenter.sell_species_at(index)
        assert state.money == 100

    def test_sell_species_without_a_selection(self):
        state = self.bag()
        assert InventoryPresenter(state).sell_species_at(None) == "ยังไม่ได้เลือกปลา"
        assert len(state.inventory) == 3

    def test_selling_one_at_a_time_matches_selling_everything(self):
        """ขายทีละตัวจนหมดต้องได้เงินเท่ากับกดขายทั้งหมดรวดเดียว"""
        one_by_one = self.bag()
        presenter = InventoryPresenter(one_by_one)
        while one_by_one.inventory:
            presenter.sell_one(0)

        at_once = self.bag()
        at_once.sell_all()
        assert one_by_one.money == at_once.money


class TestRenameAndKeepFromTheTable:
    """แก้ไขข้อมูลผ่านตาราง — ส่วน U ของ CRUD บนหน้าจอ"""

    def bag(self):
        return make_state(money=0, fish=[
            Fish("Carp", FRESHWATER, 1.0, 40), Fish("Tuna", MARINE, 4.0, 90)])

    def test_rename_updates_the_row(self):
        state = self.bag()
        presenter = InventoryPresenter(state)
        target = presenter.fish_at(0)
        message = presenter.rename_at(0, "เจ้าอ้วน")
        assert "เจ้าอ้วน" in message
        assert target.name == "เจ้าอ้วน"

    def test_rename_rejects_a_blank_name(self):
        presenter = InventoryPresenter(self.bag())
        assert "ห้ามเว้นว่าง" in presenter.rename_at(0, "   ")

    def test_rename_rejects_a_name_that_is_too_long(self):
        presenter = InventoryPresenter(self.bag())
        assert "ยาวเกินไป" in presenter.rename_at(0, "x" * 30)

    def test_rename_without_a_selection(self):
        presenter = InventoryPresenter(self.bag())
        assert presenter.rename_at(None, "เจ้าอ้วน") == "ยังไม่ได้เลือกปลา"

    def test_toggle_keep_marks_and_unmarks(self):
        presenter = InventoryPresenter(self.bag())
        assert "เก็บ" in presenter.toggle_keep_at(0)
        assert "ยกเลิก" in presenter.toggle_keep_at(0)

    def test_kept_fish_shows_a_star_in_the_table(self):
        presenter = InventoryPresenter(self.bag())
        presenter.toggle_keep_at(0)
        assert any(row[0].startswith("★") for row in presenter.visible_rows())

    def test_button_label_follows_the_selected_fish(self):
        presenter = InventoryPresenter(self.bag())
        assert presenter.keep_label_at(0) == "เก็บไว้ไม่ขาย"
        presenter.toggle_keep_at(0)
        assert presenter.keep_label_at(0) == "ยกเลิกการเก็บ"

    def test_button_label_without_a_selection(self):
        presenter = InventoryPresenter(self.bag())
        assert presenter.keep_label_at(None) == "เก็บไว้ไม่ขาย"

    def test_selling_a_kept_fish_shows_a_message_not_a_crash(self):
        state = self.bag()
        presenter = InventoryPresenter(state)
        presenter.toggle_keep_at(0)
        message = presenter.sell_one(0)
        assert "ถูกเก็บไว้" in message
        assert len(state.inventory) == 2

    def test_sell_all_reports_the_kept_ones(self):
        state = self.bag()
        presenter = InventoryPresenter(state)
        presenter.toggle_keep_at(0)
        assert "เก็บไว้ 1 ตัว" in presenter.sell_all()

    def test_sell_all_when_every_fish_is_kept(self):
        state = self.bag()
        presenter = InventoryPresenter(state)
        presenter.toggle_keep_at(0)
        presenter.toggle_keep_at(0)
        for index in range(2):
            presenter.toggle_keep_at(index)
        assert presenter.sell_all() == "ไม่มีปลาที่ขายได้ ทุกตัวถูกเก็บไว้"
