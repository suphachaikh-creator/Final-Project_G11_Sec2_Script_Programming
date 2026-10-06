"""Unit tests ของเครื่องมือปล่อยเวอร์ชัน `tools/release.py` (Final Sprint)

เทสต์ทั้ง CHANGELOG ตัวอย่างและ CHANGELOG จริงของโปรเจกต์
เคสสุดท้ายจึงแดงทันทีถ้าใครแก้ `__version__` แล้วลืมเขียน CHANGELOG
"""

import os
import sys

import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "tools"))

import release  # noqa: E402  (tools/ ไม่ใช่ package จึงต้องเพิ่ม path ก่อน)
from src import __version__  # noqa: E402

SAMPLE = """# CHANGELOG

| เวอร์ชัน | สปรินต์ |
|---|---|

---

## [1.1.0] — Patch

### แก้ไข
- แก้บั๊ก

---

## [1.0.0] — Final Sprint

### เพิ่มเข้ามา
- ของใหม่
"""


class TestChangelogSection:
    def test_lists_versions_from_top_to_bottom(self):
        assert release.changelog_versions(SAMPLE) == ["1.1.0", "1.0.0"]

    def test_section_stops_before_the_next_version(self):
        section = release.changelog_section(SAMPLE, "1.1.0")
        assert section.startswith("## [1.1.0]")
        assert "แก้บั๊ก" in section
        assert "1.0.0" not in section

    def test_trailing_divider_is_removed(self):
        assert not release.changelog_section(SAMPLE, "1.1.0").endswith("---")

    def test_last_section_runs_to_the_end(self):
        assert "ของใหม่" in release.changelog_section(SAMPLE, "1.0.0")

    def test_missing_version(self):
        assert release.changelog_section(SAMPLE, "9.9.9") is None


class TestProblems:
    def test_ready_when_everything_matches(self):
        assert release.problems("v1.1.0", "1.1.0", SAMPLE) == []

    @pytest.mark.parametrize("tag", ["1.1.0", "v1.1", "release-1"])
    def test_tag_must_look_like_a_version(self, tag):
        assert "ต้องอยู่ในรูป" in release.problems(tag, "1.1.0", SAMPLE)[0]

    def test_forgot_to_bump_the_code_version(self):
        found = release.problems("v1.1.0", "1.0.0", SAMPLE)
        assert any("__version__" in item for item in found)

    def test_forgot_to_write_the_changelog(self):
        found = release.problems("v1.2.0", "1.2.0", SAMPLE)
        assert any("ยังไม่มีหัวข้อ" in item for item in found)

    def test_changelog_entry_must_be_on_top(self):
        found = release.problems("v1.0.0", "1.0.0", SAMPLE)
        assert any("หัวข้อบนสุด" in item for item in found)


class TestThisProject:
    def test_code_version_matches_the_top_of_the_real_changelog(self):
        """ทำให้ `__version__` กับ CHANGELOG.md ไม่มีทางเดินแยกกันโดยไม่มีใครรู้"""
        with open(os.path.join(BASE_DIR, "CHANGELOG.md"), encoding="utf-8") as handle:
            text = handle.read()
        assert release.problems(f"v{__version__}", __version__, text) == []

    def test_cli_check_and_notes(self, capsys):
        assert release.main(["release.py", "check", f"v{__version__}"]) == 0
        assert release.main(["release.py", "notes", f"v{__version__}"]) == 0
        assert f"## [{__version__}]" in capsys.readouterr().out

    def test_cli_rejects_a_wrong_tag(self):
        assert release.main(["release.py", "check", "v99.0.0"]) == 1

    def test_cli_usage(self):
        assert release.main(["release.py"]) == 2
