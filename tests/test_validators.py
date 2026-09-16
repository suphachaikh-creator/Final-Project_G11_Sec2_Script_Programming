"""Unit tests ของชั้นตรวจสอบอินพุต (Sprint 1)"""

import pytest

from src.validators import (
    is_back_command,
    is_quit_command,
    normalize_command,
    validate_menu_choice,
    validate_qte_key,
    validate_search_keyword,
)


class TestNormalizeCommand:
    def test_strips_and_lowercases(self):
        assert normalize_command("  Quit  ") == "quit"

    def test_accepts_non_string(self):
        assert normalize_command(3) == "3"


class TestBackAndQuit:
    @pytest.mark.parametrize("raw", ["b", "B", " back ", "กลับ"])
    def test_back_is_case_insensitive(self, raw):
        assert is_back_command(raw) is True

    @pytest.mark.parametrize("raw", ["q", "QUIT", "exit", "ออก"])
    def test_quit_is_case_insensitive(self, raw):
        assert is_quit_command(raw) is True

    @pytest.mark.parametrize("raw", ["1", "", "bbb"])
    def test_other_input_is_neither(self, raw):
        assert is_back_command(raw) is False
        assert is_quit_command(raw) is False


class TestValidateMenuChoice:
    def test_accepts_value_in_range(self):
        assert validate_menu_choice(" 3 ", 1, 4) == 3

    def test_rejects_empty_input(self):
        with pytest.raises(ValueError, match="ห้ามเว้นว่าง"):
            validate_menu_choice("   ", 1, 4)

    @pytest.mark.parametrize("raw", ["abc", "2.5", "-1"])
    def test_rejects_non_integer(self, raw):
        with pytest.raises(ValueError):
            validate_menu_choice(raw, 1, 4)

    def test_rejects_superscript_digit(self):
        """'²' ผ่าน .isdigit() แต่ int() แปลงไม่ได้ จึงต้องถูกปฏิเสธก่อนถึง int()"""
        with pytest.raises(ValueError):
            validate_menu_choice("²", 1, 4)

    def test_accepts_thai_numeral(self):
        """เลขไทยแปลงเป็น int ได้ตามปกติ จึงยอมรับได้"""
        assert validate_menu_choice("๑", 1, 4) == 1

    @pytest.mark.parametrize("raw", ["0", "9"])
    def test_rejects_out_of_range(self, raw):
        with pytest.raises(ValueError):
            validate_menu_choice(raw, 1, 4)


class TestValidateQteKey:
    def test_accepts_matching_key(self):
        assert validate_qte_key(" K ", "k") is True

    def test_detects_wrong_key(self):
        assert validate_qte_key("x", "k") is False

    @pytest.mark.parametrize("raw", ["", "ab"])
    def test_rejects_wrong_length(self, raw):
        with pytest.raises(ValueError, match="ครั้งละหนึ่งตัว"):
            validate_qte_key(raw, "k")


class TestValidateSearchKeyword:
    def test_accepts_and_trims(self):
        assert validate_search_keyword("  tuna  ") == "tuna"

    def test_rejects_empty(self):
        with pytest.raises(ValueError, match="ห้ามเว้นว่าง"):
            validate_search_keyword("   ")

    def test_rejects_too_long(self):
        with pytest.raises(ValueError):
            validate_search_keyword("x" * 31)
