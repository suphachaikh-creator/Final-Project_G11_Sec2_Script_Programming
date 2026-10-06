"""Unit tests ของระบบปรับความยากอัตโนมัติ (Final Sprint)

ประเด็นสำคัญที่สุดคือ **เวลาต้องไม่ต่ำกว่าขั้นต่ำ** ไม่ว่าผู้เล่นจะเก่งแค่ไหน
ไม่อย่างนั้นระบบจะบีบจนเกมเล่นไม่ได้
"""

import pytest

from src.difficulty import (EASY, HARD, MAX_HISTORY, MAX_TIME_LIMIT, NORMAL,
                            DifficultyTuner, clamp, hit_rate)
from src.game_state import GameState
from src.minigame import MAX_TARGET_LENGTH, MIN_TARGET_LENGTH, MIN_TIME_LIMIT


def rounds_at(rate, count=5, total=10):
    """สร้างผลเล่นย้อนหลังที่มีอัตราการกดทันตามที่ต้องการ"""
    return [{"hits": int(total * rate), "total": total, "success": rate >= 1.0}
            for _ in range(count)]


class TestHitRate:
    def test_no_rounds_means_zero(self):
        assert hit_rate([]) == 0.0

    def test_counts_across_every_round(self):
        assert hit_rate([{"hits": 5, "total": 10},
                         {"hits": 5, "total": 10}]) == 0.5

    def test_ignores_rounds_with_no_targets(self):
        """รอบที่ total เป็น 0 ต้องไม่ทำให้หารด้วยศูนย์"""
        assert hit_rate([{"hits": 0, "total": 0}]) == 0.0

    def test_handles_missing_fields(self):
        assert hit_rate([{}, {"hits": 4, "total": 8}]) == 0.5


class TestClamp:
    @pytest.mark.parametrize("value,expected", [(-5, 0), (5, 5), (15, 10)])
    def test_keeps_value_inside_the_range(self, value, expected):
        assert clamp(value, 0, 10) == expected


class TestLevel:
    def test_stays_normal_until_there_is_enough_data(self):
        """เล่นไม่กี่รอบยังตัดสินไม่ได้ ต้องไม่รีบปรับความยาก"""
        assert DifficultyTuner(rounds_at(1.0, count=1)).level() == NORMAL

    def test_hard_when_the_player_hits_almost_everything(self):
        assert DifficultyTuner(rounds_at(1.0)).level() == HARD

    def test_easy_when_the_player_keeps_missing(self):
        assert DifficultyTuner(rounds_at(0.2)).level() == EASY

    def test_normal_in_between(self):
        assert DifficultyTuner(rounds_at(0.6)).level() == NORMAL

    def test_only_recent_rounds_count(self):
        """เล่นแย่ตอนแรกแล้วเก่งขึ้น ต้องปรับตามฝีมือปัจจุบัน"""
        tuner = DifficultyTuner(rounds_at(0.1, count=10) + rounds_at(1.0, count=5))
        assert tuner.level() == HARD


class TestTimeLimit:
    def test_hard_players_get_less_time(self):
        easy = DifficultyTuner(rounds_at(0.2)).time_limit_for(3)
        hard = DifficultyTuner(rounds_at(1.0)).time_limit_for(3)
        assert hard < easy

    def test_never_drops_below_the_floor(self):
        """แม้ผู้เล่นเก่งมากและคันเบ็ดเลเวลต่ำ เวลาก็ต้องไม่ต่ำกว่าขั้นต่ำ"""
        tuner = DifficultyTuner(rounds_at(1.0))
        for rod_level in range(1, 10):
            assert tuner.time_limit_for(rod_level) >= MIN_TIME_LIMIT

    def test_never_rises_above_the_ceiling(self):
        tuner = DifficultyTuner(rounds_at(0.1))
        for rod_level in range(1, 30):
            assert tuner.time_limit_for(rod_level) <= MAX_TIME_LIMIT

    def test_normal_players_keep_the_original_time(self):
        from src.minigame import QTEMinigame
        tuner = DifficultyTuner(rounds_at(0.6))
        assert tuner.time_limit_for(2) == QTEMinigame.time_limit_for(2)


class TestTargetLength:
    def test_hard_players_get_longer_targets(self):
        easy = DifficultyTuner(rounds_at(0.2)).target_length_for(3)
        hard = DifficultyTuner(rounds_at(1.0)).target_length_for(3)
        assert hard > easy

    def test_stays_inside_the_range_the_minigame_supports(self):
        for rate in (0.0, 0.5, 1.0):
            tuner = DifficultyTuner(rounds_at(rate))
            for rod_level in range(1, 20):
                length = tuner.target_length_for(rod_level)
                assert MIN_TARGET_LENGTH <= length <= MAX_TARGET_LENGTH


class TestRecording:
    def test_record_appends_a_round(self):
        tuner = DifficultyTuner()
        assert tuner.record({"hits": 3, "total": 5}) == 1

    def test_record_copies_the_result(self):
        """เก็บสำเนาไว้ ไม่ให้ผู้เรียกแก้ประวัติย้อนหลังได้"""
        result = {"hits": 3, "total": 5}
        tuner = DifficultyTuner()
        tuner.record(result)
        result["hits"] = 99
        assert tuner.rounds[0]["hits"] == 3

    def test_settings_report_everything_the_next_round_needs(self):
        settings = DifficultyTuner(rounds_at(1.0)).settings_for(2)
        assert settings["level"] == HARD
        assert set(settings) == {"level", "hit_rate", "time_limit", "target_length"}


class TestSerialization:
    def test_round_trip(self):
        tuner = DifficultyTuner(rounds_at(0.5, count=3))
        restored = DifficultyTuner.from_dict(tuner.to_dict())
        assert restored.rounds == tuner.rounds

    @pytest.mark.parametrize("data", [None, {}, {"rounds": "ไม่ใช่ลิสต์"}])
    def test_broken_save_data_starts_empty_instead_of_crashing(self, data):
        assert DifficultyTuner.from_dict(data).rounds == []


class TestApplyTo:
    """ปรับมินิเกมจากภายนอกโดยไม่ต้องแก้ minigame.py"""

    def make_minigame(self, rod_level=2):
        from src.minigame import QTEMinigame

        class Rng:
            def randint(self, low, high):
                return low

            def choice(self, options):
                return options[0]

        return QTEMinigame(rod_level, rng=Rng()), Rng()

    def test_sets_the_time_limit_from_the_tuner(self):
        minigame, rng = self.make_minigame()
        tuner = DifficultyTuner(rounds_at(1.0))
        tuner.apply_to(minigame, 2, rng=rng)
        assert minigame.time_limit == tuner.time_limit_for(2)

    def test_sets_the_number_of_targets(self):
        minigame, rng = self.make_minigame()
        tuner = DifficultyTuner(rounds_at(1.0))
        tuner.apply_to(minigame, 2, rng=rng)
        assert minigame.total_targets == tuner.target_length_for(2)

    def test_returns_the_settings_used(self):
        minigame, rng = self.make_minigame()
        settings = DifficultyTuner(rounds_at(0.2)).apply_to(minigame, 2, rng=rng)
        assert settings["level"] == EASY

    def test_good_players_get_more_targets_than_weak_ones(self):
        hard_game, rng = self.make_minigame()
        easy_game, _ = self.make_minigame()
        DifficultyTuner(rounds_at(1.0)).apply_to(hard_game, 3, rng=rng)
        DifficultyTuner(rounds_at(0.2)).apply_to(easy_game, 3, rng=rng)
        assert hard_game.total_targets > easy_game.total_targets

    def test_the_minigame_is_still_playable_afterwards(self):
        """ปรับแล้วต้องยังเล่นได้จริง ไม่ใช่แค่ตัวเลขเปลี่ยน"""
        minigame, rng = self.make_minigame()
        DifficultyTuner(rounds_at(1.0)).apply_to(minigame, 2, rng=rng)
        minigame.start()
        assert minigame.submit(minigame.current_target) is True


class TestSaveFileSize:
    """ประวัติอยู่ในไฟล์เซฟหลัก จึงต้องไม่โตขึ้นเรื่อยๆ"""

    def test_record_keeps_only_the_latest_rounds(self):
        tuner = DifficultyTuner()
        for index in range(MAX_HISTORY + 15):
            tuner.record({"hits": index, "total": 100})
        assert len(tuner.rounds) == MAX_HISTORY
        assert tuner.rounds[-1]["hits"] == MAX_HISTORY + 14

    def test_long_history_from_an_old_save_is_trimmed(self):
        tuner = DifficultyTuner.from_dict({"rounds": [{"hits": 1, "total": 1}] * 100})
        assert len(tuner.rounds) == MAX_HISTORY

    def test_history_survives_the_main_save_file(self):
        state = GameState()
        tuner = DifficultyTuner(rounds_at(1.0))
        state.difficulty_data = tuner.to_dict()
        loaded = GameState.from_dict(state.to_dict())
        assert DifficultyTuner.from_dict(loaded.difficulty_data).level() == HARD

    @pytest.mark.parametrize("broken", [[1, 2], "oops", None])
    def test_broken_difficulty_data_in_the_save_does_not_crash(self, broken):
        state = GameState.from_dict({"difficulty_data": broken})
        assert state.difficulty_data == {}
        assert DifficultyTuner.from_dict(state.difficulty_data).level() == NORMAL
