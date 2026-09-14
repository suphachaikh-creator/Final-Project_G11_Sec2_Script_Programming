"""Unit tests ของ File I/O - ใช้ tmp_path จึงไม่แตะไฟล์เซฟจริง"""

import json
import os

import pytest

from src import app_functions
from src.pet import Pet


@pytest.fixture
def temp_save(tmp_path, monkeypatch):
    """ชี้ปลายทางการบันทึกไปที่โฟลเดอร์ชั่วคราวของเทสต์"""
    save_dir = tmp_path / "data"
    monkeypatch.setattr(app_functions, "SAVE_DIR", str(save_dir))
    monkeypatch.setattr(app_functions, "SAVE_FILE", str(save_dir / "pet_state.json"))
    return save_dir / "pet_state.json"


@pytest.fixture
def pet():
    return Pet("มิว", "Siamese", "ไทย", "ขี้อ้อน", 50, "แมวไทยโบราณ")


def test_load_returns_none_when_file_missing(temp_save):
    assert app_functions.load_game() is None


def test_save_creates_file_and_directory(temp_save, pet):
    app_functions.save_game(pet)
    assert os.path.exists(temp_save)


def test_save_writes_readable_utf8_json(temp_save, pet):
    app_functions.save_game(pet)
    with open(temp_save, encoding="utf-8") as saved_file:
        data = json.load(saved_file)
    assert data["name"] == "มิว"


def test_round_trip_restores_stats(temp_save, pet):
    pet.feed()
    pet.play()
    app_functions.save_game(pet)

    restored = app_functions.load_game()
    assert restored is not None
    assert restored.to_dict() == pet.to_dict()


def test_load_returns_none_when_file_is_corrupted(temp_save):
    temp_save.parent.mkdir(parents=True, exist_ok=True)
    temp_save.write_text("{ ไฟล์เสีย", encoding="utf-8")
    assert app_functions.load_game() is None


def test_fetch_new_pets_returns_empty_list_on_error(monkeypatch, capsys):
    def _boom(*args, **kwargs):
        raise RuntimeError("API ล่ม")

    monkeypatch.setattr(app_functions.APIClient, "get_cats_from_gemini", _boom)
    assert app_functions.fetch_new_pets() == []
    assert "เกิดข้อผิดพลาดในการดึง API" in capsys.readouterr().out
