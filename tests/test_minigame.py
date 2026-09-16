"""Unit tests ของมินิเกม QTE (Sprint 2)

ทุกเทสต์ใช้นาฬิกาจำลอง จึงรันเสร็จทันทีโดยไม่ต้องรอเวลาจริง
"""

import pytest

from src.minigame import MIN_TIME_LIMIT, QTEMinigame


class FakeClock:
    """นาฬิกาจำลองที่เดินหน้าได้ตามสั่ง"""

    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


class ScriptedRandom:
    """ตัวสุ่มปลอมที่ให้โจทย์ตายตัว"""

    def __init__(self, length=3, letter="a"):
        self.length = length
        self.letter = letter

    def randint(self, low, high):
        return self.length

    def choice(self, sequence):
        return self.letter


@pytest.fixture
def clock():
    return FakeClock()


@pytest.fixture
def game(clock):
    return QTEMinigame(rod_level=2, rng=ScriptedRandom(length=3), clock=clock)


class TestTimeLimit:
    def test_higher_rod_level_gives_more_time(self):
        assert QTEMinigame.time_limit_for(2) > QTEMinigame.time_limit_for(1)

    def test_never_below_minimum(self):
        assert QTEMinigame.time_limit_for(0) >= MIN_TIME_LIMIT


class TestTargets:
    def test_builds_targets_from_rng(self, game):
        assert game.total_targets == 3
        assert game.targets == ["a", "a", "a"]

    def test_current_target_is_none_when_complete(self, game):
        game.start()
        for _ in range(3):
            game.submit("a")
        assert game.is_complete is True
        assert game.current_target is None


class TestSubmit:
    def test_correct_key_counts_as_hit(self, game):
        game.start()
        assert game.submit("a") is True
        assert game.hit_count == 1

    def test_key_is_case_insensitive(self, game):
        game.start()
        assert game.submit(" A ") is True

    def test_wrong_key_counts_as_miss(self, game):
        game.start()
        assert game.submit("z") is False
        assert game.miss_count == 1
        assert game.hit_count == 0

    def test_correct_key_grants_extra_time(self, game, clock):
        game.start()
        clock.advance(3.0)
        before = game.time_left()
        game.submit("a")
        assert game.time_left() > before


class TestTimeout:
    def test_time_left_never_negative(self, game, clock):
        game.start()
        clock.advance(999)
        assert game.time_left() == 0.0

    def test_times_out_after_limit(self, game, clock):
        game.start()
        clock.advance(game.time_limit + 0.1)
        assert game.is_timed_out() is True

    def test_submit_is_ignored_after_timeout(self, game, clock):
        game.start()
        clock.advance(999)
        assert game.submit("a") is False
        assert game.hit_count == 0

    def test_full_time_before_start(self, game):
        assert game.time_left() == game.time_limit


class TestResult:
    def test_success_when_all_targets_hit(self, game):
        game.start()
        for _ in range(3):
            game.submit("a")
        assert game.result() == {"success": True, "hits": 3, "misses": 0, "total": 3}

    def test_failure_when_timed_out(self, game, clock):
        game.start()
        game.submit("a")
        clock.advance(999)
        result = game.result()
        assert result["success"] is False
        assert result["hits"] == 1
