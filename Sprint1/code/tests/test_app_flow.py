"""Integration tests ของหน้าจอ CLI โดยจำลองการพิมพ์ของผู้ใช้"""

import builtins

import pytest

from src import app


@pytest.fixture
def fake_input(monkeypatch):
    """แทนที่ input() ด้วยลำดับคำสั่งที่กำหนดไว้ล่วงหน้า"""

    def _install(commands):
        queue = list(commands)

        def _fake(prompt=""):
            if not queue:
                raise EOFError
            return queue.pop(0)

        monkeypatch.setattr(builtins, "input", _fake)

    return _install


def test_quit_exits_immediately(fake_input, capsys):
    fake_input(["QUIT"])
    app.run_app()
    output = capsys.readouterr().out
    assert "ขอบคุณที่ทดลองใช้ PixelPaw" in output


def test_invalid_menu_choice_does_not_crash(fake_input, capsys):
    fake_input(["abc", "99", "quit"])
    app.run_app()
    output = capsys.readouterr().out
    assert output.count("[X]") == 2
    assert "ขอบคุณที่ทดลองใช้ PixelPaw" in output


def test_status_requires_adoption_first(fake_input, capsys):
    fake_input(["2", "quit"])
    app.run_app()
    assert "ยังไม่มีน้องแมว" in capsys.readouterr().out


def test_adopt_then_show_status(fake_input, capsys):
    fake_input(["1", "1", "มิว", "3", "2", "quit"])
    app.run_app()
    output = capsys.readouterr().out
    assert "รับเลี้ยง 'มิว' เรียบร้อย" in output
    assert "Siamese" in output
    assert "อายุ" in output


def test_care_menu_shows_pending_feature(fake_input, capsys):
    fake_input(["1", "1", "มิว", "3", "3", "1", "4", "quit"])
    app.run_app()
    output = capsys.readouterr().out
    assert "[Sprint 2]" in output
    assert "กลับสู่เมนูหลัก" in output


def test_menu_exit_option_ends_program(fake_input, capsys):
    fake_input(["4"])
    app.run_app()
    assert "ขอบคุณที่ทดลองใช้ PixelPaw" in capsys.readouterr().out
