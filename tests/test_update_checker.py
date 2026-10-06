"""Unit tests ของการตรวจเวอร์ชันใหม่ (Final Sprint)

ไม่มีเทสต์ใดยิง GitHub จริงหรือสร้างเธรดจริง — ใช้ `FakeHttp` และ `spawn` ที่รันทันที
"""

import pytest
import requests

from src import __version__
from src.gui.presenter import DashboardPresenter
from src.game_state import GameState
from src.update_checker import (AVAILABLE, CHECKING, LATEST, LATEST_RELEASE_API,
                                RELEASES_PAGE, UNKNOWN, UpdateChecker, parse_version)


class FakeResponse:
    def __init__(self, payload=None, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def json(self):
        if self._payload is None:
            raise ValueError("ไม่ใช่ JSON")
        return self._payload


class FakeHttp:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.calls = []

    def get(self, url, headers=None, timeout=None):
        self.calls.append((url, timeout))
        if self.error:
            raise self.error
        return self.response


def release(tag, url="https://github.com/x/y/releases/tag/v9"):
    return FakeResponse({"tag_name": tag, "html_url": url})


def checker(response=None, error=None, current="1.0.0"):
    return UpdateChecker(current=current, http=FakeHttp(response, error))


class TestParseVersion:
    @pytest.mark.parametrize("text,expected", [
        ("v1.0.0", (1, 0, 0)), ("1.2.3", (1, 2, 3)), ("V2.10.0", (2, 10, 0))])
    def test_valid(self, text, expected):
        assert parse_version(text) == expected

    @pytest.mark.parametrize("text", ["", "v1.0", "1.0.0.0", "v1.x.0", "latest", None, 100])
    def test_invalid(self, text):
        assert parse_version(text) is None

    def test_compares_numbers_not_text(self):
        """"1.10.0" ต้องใหม่กว่า "1.9.0" ถ้าเทียบเป็นข้อความจะผิด"""
        assert parse_version("1.10.0") > parse_version("1.9.0")


class TestCheck:
    def test_newer_release_is_available(self):
        updates = checker(release("v1.1.0"))
        assert updates.check() == AVAILABLE
        assert updates.update_available is True
        assert updates.latest == "1.1.0"

    def test_same_version_is_latest(self):
        assert checker(release("v1.0.0")).check() == LATEST

    def test_older_release_is_not_an_update(self):
        """เล่นเวอร์ชันที่ยังไม่ได้ปล่อย (เช่นตอนพัฒนา) ต้องไม่ถูกบอกให้ถอยไปรุ่นเก่า"""
        assert checker(release("v0.7.0")).check() == LATEST

    def test_uses_the_release_page_from_github(self):
        updates = checker(release("v2.0.0", url="https://github.com/a/b/releases/tag/v2.0.0"))
        updates.check()
        assert updates.url.endswith("/v2.0.0")

    def test_falls_back_to_the_latest_page_when_url_is_missing(self):
        updates = checker(FakeResponse({"tag_name": "v2.0.0"}))
        updates.check()
        assert updates.url == RELEASES_PAGE

    def test_asks_the_latest_release_endpoint_with_a_timeout(self):
        updates = checker(release("v1.0.0"))
        updates.check()
        url, timeout = updates.http.calls[0]
        assert url == LATEST_RELEASE_API
        assert timeout and timeout <= 10


class TestNeverCrashes:
    @pytest.mark.parametrize("error", [
        requests.exceptions.ConnectionError("ไม่มีเน็ต"),
        requests.exceptions.Timeout("ช้า"),
    ])
    def test_network_problems(self, error):
        updates = checker(error=error)
        assert updates.check() == UNKNOWN
        assert "เชื่อมต่อ GitHub ไม่ได้" in updates.last_error

    def test_no_release_yet(self):
        updates = checker(FakeResponse(status_code=404))
        assert updates.check() == UNKNOWN
        assert "ยังไม่มี release" in updates.last_error

    def test_rate_limited(self):
        updates = checker(FakeResponse(status_code=403))
        assert updates.check() == UNKNOWN
        assert "403" in updates.last_error

    @pytest.mark.parametrize("response", [
        FakeResponse(None), FakeResponse({"name": "no tag"}), FakeResponse(["list"]),
        release("nightly"),
    ])
    def test_bad_answers(self, response):
        assert checker(response).check() == UNKNOWN

    def test_bad_current_version(self):
        assert checker(release("v1.0.0"), current="dev").check() == UNKNOWN


class TestBackground:
    def test_start_runs_the_check_through_spawn(self):
        jobs = []
        updates = UpdateChecker(http=FakeHttp(release("v9.0.0")), spawn=jobs.append)
        updates.start()
        assert updates.status == CHECKING and updates.is_complete is False
        jobs[0]()
        assert updates.is_complete is True
        assert updates.update_available is True

    def test_start_twice_checks_once(self):
        jobs = []
        updates = UpdateChecker(http=FakeHttp(release("v9.0.0")), spawn=jobs.append)
        updates.start()
        updates.start()
        assert len(jobs) == 1

    def test_not_started_is_not_complete(self):
        assert UpdateChecker(http=FakeHttp()).is_complete is False


class TestStatusText:
    def test_available(self):
        updates = checker(release("v1.1.0"))
        updates.check()
        assert "มีเวอร์ชันใหม่ v1.1.0" in updates.status_text()
        assert "v1.0.0" in updates.status_text()

    def test_latest(self):
        updates = checker(release("v1.0.0"))
        updates.check()
        assert "ล่าสุดแล้ว" in updates.status_text()

    def test_unknown_says_why(self):
        updates = checker(FakeResponse(status_code=404))
        updates.check()
        assert "ยังไม่มี release" in updates.status_text()

    def test_default_version_comes_from_the_package(self):
        assert UpdateChecker(http=FakeHttp()).status_text() == f"v{__version__}"


class TestDashboard:
    def test_shows_the_version_text(self):
        updates = checker(release("v1.1.0"))
        updates.check()
        presenter = DashboardPresenter(GameState(), updates=updates)
        assert "มีเวอร์ชันใหม่" in presenter.version_text()
        assert presenter.can_download_update() is True

    def test_no_download_button_when_up_to_date(self):
        updates = checker(release("v1.0.0"))
        updates.check()
        assert DashboardPresenter(GameState(), updates=updates).can_download_update() is False

    def test_blank_without_a_checker(self):
        presenter = DashboardPresenter(GameState())
        assert presenter.version_text() == ""
        assert presenter.can_download_update() is False
