"""Unit tests ของตัวเชื่อมต่อ Open Fisheries (Sprint 2)

API ตัวนี้ให้ **ชื่อสามัญภาษาอังกฤษ** ซึ่งเป็นข้อมูลเสริม ไม่ใช่ข้อมูลหลัก
เมื่อเรียกไม่สำเร็จจึงต้องคืน dict ว่าง แล้วให้เกมใช้ชื่อวิทยาศาสตร์แทน โดยไม่ crash
"""

import pytest
import requests

from src.openfisheries_api import OpenFisheriesAPI

SAMPLE = [
    {"scientific_name": "Carassius auratus", "english_name": "Goldfish"},
    {"scientific_name": "Salmo salar", "english_name": "Atlantic salmon"},
    {"scientific_name": "Xxx yyy", "english_name": ""},
    {"scientific_name": "", "english_name": "ไม่มีชื่อวิทย์"},
]


class FakeResponse:
    def __init__(self, payload=None, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.exceptions.HTTPError(f"status {self.status_code}")

    def json(self):
        if self._payload is None:
            raise ValueError("ไม่ใช่ JSON")
        return self._payload


class FakeHttp:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.calls = 0

    def get(self, url, headers=None, timeout=None):
        self.calls += 1
        if self.error:
            raise self.error
        return self.response


def make_api(response=None, error=None):
    return OpenFisheriesAPI(http=FakeHttp(response, error))


class TestFetchCommonNames:
    def test_builds_lookup_keyed_by_lowercase_scientific_name(self):
        names = make_api(FakeResponse(SAMPLE)).fetch_common_names()
        assert names["carassius auratus"] == "Goldfish"
        assert names["salmo salar"] == "Atlantic salmon"

    def test_skips_records_missing_either_name(self):
        names = make_api(FakeResponse(SAMPLE)).fetch_common_names()
        assert len(names) == 2

    def test_caches_result_and_calls_api_once(self):
        http = FakeHttp(FakeResponse(SAMPLE))
        api = OpenFisheriesAPI(http=http)
        api.fetch_common_names()
        api.fetch_common_names()
        assert http.calls == 1


class TestErrorHandling:
    """ทุกกรณีต้องคืน dict ว่าง ไม่โยน exception ออกมา เพราะเป็นข้อมูลเสริม"""

    def test_returns_empty_on_connection_error(self):
        api = make_api(error=requests.exceptions.ConnectionError("ปิดอยู่"))
        assert api.fetch_common_names() == {}
        assert "ConnectionError" in api.last_error

    def test_returns_empty_on_timeout(self):
        api = make_api(error=requests.exceptions.Timeout("ช้า"))
        assert api.fetch_common_names() == {}
        assert "Timeout" in api.last_error

    def test_returns_empty_on_http_error(self):
        api = make_api(FakeResponse(status_code=500))
        assert api.fetch_common_names() == {}
        assert "HTTPError" in api.last_error

    def test_returns_empty_when_body_is_not_json(self):
        api = make_api(FakeResponse(payload=None))
        assert api.fetch_common_names() == {}
        assert "JSON" in api.last_error

    @pytest.mark.parametrize("payload", [{"not": "a list"}, "ข้อความ", 42])
    def test_returns_empty_when_payload_is_not_a_list(self, payload):
        api = make_api(FakeResponse(payload))
        assert api.fetch_common_names() == {}
        assert api.last_error
