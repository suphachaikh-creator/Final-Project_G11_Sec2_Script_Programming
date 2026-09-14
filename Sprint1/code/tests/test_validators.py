"""Unit tests สำหรับ Sprint 1 - ครอบคลุม Edge Cases ตาม Definition of Done"""

import pytest

from src.validators import (
    clamp_stat,
    is_quit_command,
    normalize_command,
    validate_age,
    validate_menu_choice,
    validate_pet_name,
)


class TestNormalizeCommand:
    def test_strips_and_lowercases(self):
        assert normalize_command("  QUIT  ") == "quit"

    def test_accepts_non_string(self):
        assert normalize_command(4) == "4"


class TestIsQuitCommand:
    @pytest.mark.parametrize("raw", ["quit", "QUIT", "Quit", " quit ", "exit", "q"])
    def test_quit_is_case_insensitive(self, raw):
        assert is_quit_command(raw) is True

    @pytest.mark.parametrize("raw", ["1", "quitx", ""])
    def test_other_commands_are_not_quit(self, raw):
        assert is_quit_command(raw) is False


class TestValidateMenuChoice:
    def test_accepts_value_in_range(self):
        assert validate_menu_choice(" 3 ", 1, 4) == 3

    def test_rejects_empty_input(self):
        with pytest.raises(ValueError, match="ห้ามเว้นว่าง"):
            validate_menu_choice("   ", 1, 4)

    def test_rejects_non_numeric_input(self):
        with pytest.raises(ValueError):
            validate_menu_choice("abc", 1, 4)

    def test_rejects_value_above_range(self):
        with pytest.raises(ValueError):
            validate_menu_choice("9", 1, 4)

    def test_rejects_negative_value(self):
        with pytest.raises(ValueError):
            validate_menu_choice("-1", 1, 4)


class TestValidatePetName:
    def test_accepts_and_trims_name(self):
        assert validate_pet_name("  มิว  ") == "มิว"

    def test_rejects_empty_name(self):
        with pytest.raises(ValueError, match="ห้ามเว้นว่าง"):
            validate_pet_name("   ")

    def test_rejects_too_long_name(self):
        with pytest.raises(ValueError):
            validate_pet_name("x" * 21)


class TestValidateAge:
    def test_accepts_positive_integer(self):
        assert validate_age("3") == 3

    def test_accepts_zero(self):
        assert validate_age("0") == 0

    def test_rejects_non_numeric_age(self):
        with pytest.raises(ValueError):
            validate_age("สามปี")

    def test_rejects_negative_age(self):
        with pytest.raises(ValueError):
            validate_age("-5")

    def test_rejects_decimal_age(self):
        with pytest.raises(ValueError):
            validate_age("2.5")

    def test_rejects_unrealistic_age(self):
        with pytest.raises(ValueError):
            validate_age("99")


class TestClampStat:
    @pytest.mark.parametrize(
        "value, expected",
        [(-10, 0), (0, 0), (50, 50), (100, 100), (150, 100)],
    )
    def test_clamps_into_range(self, value, expected):
        assert clamp_stat(value) == expected
