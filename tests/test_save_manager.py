"""Unit tests ของชั้นบันทึกไฟล์ (Sprint 2)

ทุกเทสต์เขียนลง tmp_path ของ pytest จึงไม่แตะไฟล์เซฟจริงของผู้เล่น
"""

import json

import pytest

from src.fish import FRESHWATER, Fish
from src.game_state import START_MONEY, GameState
from src.save_manager import SaveManager


@pytest.fixture
def save_file(tmp_path):
    return tmp_path / "data" / "save_game.json"


@pytest.fixture
def saver(save_file):
    return SaveManager(save_file=str(save_file))


@pytest.fixture
def state():
    return GameState(
        money=280,
        inventory=[Fish("Catfish", FRESHWATER, 2.43, 36)],
        bait_level=2,
        rod_level=3,
    )


class TestSave:
    def test_creates_file_and_parent_directory(self, saver, save_file, state):
        assert saver.save(state) is True
        assert save_file.exists()

    def test_writes_readable_utf8_json(self, saver, save_file, state):
        saver.save(state)
        data = json.loads(save_file.read_text(encoding="utf-8"))
        assert data["money"] == 280
        assert data["inventory"][0]["name"] == "Catfish"

    def test_keeps_thai_characters_readable(self, saver, save_file):
        saver.save(GameState(inventory=[Fish("ปลาดุก", FRESHWATER, 1.0, 10)]))
        assert "ปลาดุก" in save_file.read_text(encoding="utf-8")


class TestLoad:
    def test_returns_none_when_file_missing(self, saver):
        assert saver.load() is None
        assert saver.last_error == "ยังไม่มีไฟล์เซฟ"

    def test_round_trip_restores_everything(self, saver, state):
        saver.save(state)
        restored = saver.load()
        assert restored is not None
        assert restored.to_dict() == state.to_dict()

    def test_returns_none_when_file_is_corrupted(self, saver, save_file):
        save_file.parent.mkdir(parents=True, exist_ok=True)
        save_file.write_text("{ ไฟล์พัง", encoding="utf-8")
        assert saver.load() is None
        assert "ไฟล์เซฟเสียหาย" in saver.last_error

    def test_returns_none_when_json_is_not_an_object(self, saver, save_file):
        save_file.parent.mkdir(parents=True, exist_ok=True)
        save_file.write_text("[1, 2, 3]", encoding="utf-8")
        assert saver.load() is None

    def test_missing_fields_fall_back_to_defaults(self, saver, save_file):
        save_file.parent.mkdir(parents=True, exist_ok=True)
        save_file.write_text('{"money": 500}', encoding="utf-8")
        restored = saver.load()
        assert restored.money == 500
        assert restored.bait_level == 1
        assert restored.inventory == []


class TestLoadOrNew:
    def test_starts_new_game_when_no_save(self, saver):
        assert saver.load_or_new().money == START_MONEY

    def test_uses_existing_save_when_available(self, saver, state):
        saver.save(state)
        assert saver.load_or_new().money == 280
