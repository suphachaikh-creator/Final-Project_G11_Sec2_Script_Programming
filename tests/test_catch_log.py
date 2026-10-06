"""Unit tests ของประวัติการจับปลาและสถิติย้อนหลัง (Final Sprint)

ใช้ `tmp_path` ทุกเคส จึงไม่แตะ `data/catch_log.jsonl` ของผู้เล่นจริง
"""

import json

import pytest

from src.catch_log import CatchLog, summarize
from src.fish import BRACKISH, FRESHWATER, MARINE, Fish
from src.game_state import GameState
from src.gui.presenter import DashboardPresenter, FishingPresenter, TkClock


def make_log(tmp_path, name="log.jsonl"):
    return CatchLog(str(tmp_path / name), clock=lambda: "2026-10-06T09:00:00")


def entry(name="Carp", location=FRESHWATER, weight=1.0, price=10):
    return {"name": name, "location": location, "weight_kg": weight,
            "price": price, "caught_at": "2026-10-06T09:00:00"}


class TestRecord:
    def test_creates_the_file_and_folder(self, tmp_path):
        log = make_log(tmp_path / "data")
        assert log.record(Fish("Carp", FRESHWATER, 1.5, 30)) is True
        assert (tmp_path / "data" / "log.jsonl").exists()

    def test_one_line_per_fish(self, tmp_path):
        log = make_log(tmp_path)
        log.record(Fish("Carp", FRESHWATER, 1.5, 30))
        log.record(Fish("Tuna", MARINE, 4.0, 90))
        lines = (tmp_path / "log.jsonl").read_text(encoding="utf-8").splitlines()
        assert len(lines) == 2
        assert json.loads(lines[1])["name"] == "Tuna"

    def test_append_only_never_rewrites_old_lines(self, tmp_path):
        log = make_log(tmp_path)
        log.record(Fish("Carp", FRESHWATER, 1.5, 30))
        first = (tmp_path / "log.jsonl").read_text(encoding="utf-8")
        CatchLog(log.log_file).record(Fish("Tuna", MARINE, 4.0, 90))
        assert (tmp_path / "log.jsonl").read_text(encoding="utf-8").startswith(first)

    def test_keeps_thai_names_readable(self, tmp_path):
        log = make_log(tmp_path)
        log.record(Fish("ปลานิล", FRESHWATER, 1.0, 20))
        assert "ปลานิล" in (tmp_path / "log.jsonl").read_text(encoding="utf-8")

    def test_stores_the_time_from_the_injected_clock(self, tmp_path):
        log = make_log(tmp_path)
        log.record(Fish("Carp", FRESHWATER, 1.0, 10))
        assert log.entries()[0]["caught_at"] == "2026-10-06T09:00:00"

    def test_failing_to_write_does_not_raise(self, tmp_path):
        """ใช้โฟลเดอร์เป็นชื่อไฟล์ เขียนไม่ได้แน่นอน"""
        (tmp_path / "taken").mkdir()
        log = CatchLog(str(tmp_path / "taken"))
        assert log.record(Fish("Carp", FRESHWATER, 1.0, 10)) is False
        assert "บันทึกประวัติไม่สำเร็จ" in log.last_error


class TestHistoryOutlivesSelling:
    def test_selling_the_bag_does_not_erase_the_history(self, tmp_path):
        log = make_log(tmp_path)
        state = GameState()
        for fish in (Fish("Carp", FRESHWATER, 1.0, 10), Fish("Tuna", MARINE, 3.0, 50)):
            state.add_fish(fish)
            log.record(fish)
        state.sell_all()
        assert state.inventory == []
        assert log.summary()["count"] == 2


class TestEntries:
    def test_missing_file_means_no_history(self, tmp_path):
        assert make_log(tmp_path).entries() == []

    def test_broken_lines_are_skipped_not_fatal(self, tmp_path):
        good = json.dumps(entry())
        (tmp_path / "log.jsonl").write_text(
            "\n".join([good, "{ขาดครึ่ง", "[1, 2]", good, ""]), encoding="utf-8")
        log = make_log(tmp_path)
        assert len(log.entries()) == 2
        assert log.skipped == 2

    @pytest.mark.parametrize("bad", [
        {"location": FRESHWATER, "weight_kg": 1.0, "price": 10},
        entry(name="  "),
        entry(weight="หนัก"),
        entry(price=None),
        entry(location="moon"),
    ])
    def test_entries_with_wrong_fields_are_skipped(self, tmp_path, bad):
        (tmp_path / "log.jsonl").write_text(json.dumps(bad), encoding="utf-8")
        log = make_log(tmp_path)
        assert log.entries() == []
        assert log.skipped == 1


class TestSummarize:
    def test_empty_history(self):
        stats = summarize([])
        assert stats["count"] == 0
        assert stats["most_common"] is None
        assert set(stats["by_location"]) == {FRESHWATER, MARINE, BRACKISH}

    def test_totals_and_average(self):
        stats = summarize([entry(weight=1.0, price=10), entry(weight=2.5, price=40)])
        assert stats["count"] == 2
        assert stats["total_weight"] == 3.5
        assert stats["average_weight"] == 1.75
        assert stats["total_value"] == 50

    def test_most_common_species(self):
        stats = summarize([entry("Carp"), entry("Tuna", MARINE), entry("Carp")])
        assert stats["most_common"] == ("Carp", 2)

    def test_tie_goes_to_the_species_caught_first(self):
        stats = summarize([entry("Tuna", MARINE), entry("Carp")])
        assert stats["most_common"] == ("Tuna", 1)

    def test_heaviest(self):
        stats = summarize([entry(weight=1.0), entry("Tuna", MARINE, weight=9.1)])
        assert stats["heaviest"]["name"] == "Tuna"

    def test_split_by_location(self):
        stats = summarize([entry(price=10), entry(price=20),
                           entry("Tuna", MARINE, price=90)])
        assert stats["by_location"][FRESHWATER] == {"count": 2, "value": 30}
        assert stats["by_location"][MARINE] == {"count": 1, "value": 90}
        assert stats["by_location"][BRACKISH] == {"count": 0, "value": 0}


class FakeApi:
    def random_species(self, location, rng=None):
        return {"name": "Goldfish", "location": location}


class FakeRng:
    def randint(self, low, high):
        return 2

    def choice(self, options):
        return "a"

    def uniform(self, low, high):
        return 2.0


class TestFishingPresenterRecordsCatches:
    def play(self, catch_log, win=True):
        presenter = FishingPresenter(GameState(), FakeApi(), rng=FakeRng(),
                                     clock=TkClock(1000), catch_log=catch_log)
        presenter.start(FRESHWATER)
        if win:
            presenter.press("a")
            presenter.press("a")
        else:
            for _ in range(50):
                presenter.clock.tick()
        return presenter.finish()

    def test_a_caught_fish_is_written_to_the_log(self, tmp_path):
        log = make_log(tmp_path)
        result = self.play(log)
        assert result["success"] is True
        assert log.entries()[0]["name"] == "Goldfish"

    def test_a_lost_fish_is_not_written(self, tmp_path):
        log = make_log(tmp_path)
        self.play(log, win=False)
        assert log.entries() == []

    def test_works_without_a_log(self):
        assert self.play(None)["success"] is True


class TestDashboardHistory:
    def test_blank_without_a_log(self):
        assert DashboardPresenter(GameState()).history_lines() == []

    def test_invites_the_player_when_there_is_no_history(self, tmp_path):
        lines = DashboardPresenter(GameState(), catch_log=make_log(tmp_path)).history_lines()
        assert "ยังไม่มีประวัติ" in lines[0]

    def test_shows_the_summary(self, tmp_path):
        log = make_log(tmp_path)
        log.record(Fish("Carp", FRESHWATER, 1.0, 10))
        log.record(Fish("Carp", FRESHWATER, 2.0, 30))
        log.record(Fish("Tuna", MARINE, 9.1, 90))
        lines = DashboardPresenter(GameState(), catch_log=log).history_lines()
        assert "จับได้ทั้งหมด 3 ตัว" in lines[0]
        assert "Carp (2 ครั้ง)" in lines[1]
        assert "Tuna 9.1 กก." in lines[1]
        assert "มูลค่ารวม $130" in lines[2]
        assert "ทะเลลึก 1 ตัว $90" in lines[2]

    def test_mentions_broken_lines(self, tmp_path):
        (tmp_path / "log.jsonl").write_text(json.dumps(entry()) + "\n{เสีย\n",
                                            encoding="utf-8")
        lines = DashboardPresenter(GameState(), catch_log=make_log(tmp_path)).history_lines()
        assert "ข้ามประวัติที่เสีย 1 บรรทัด" in lines[-1]
