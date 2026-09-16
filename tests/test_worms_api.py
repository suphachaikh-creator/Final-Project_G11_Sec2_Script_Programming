"""Unit tests ของตัวเชื่อมต่อ WoRMS (Sprint 2)

ไม่มีเทสต์ใดที่ยิงเครือข่ายจริง ใช้ตัวปลอมแทน `requests` ทั้งหมด
"""

import pytest
import requests

from src.fish import BRACKISH, FRESHWATER, MARINE
from src.worms_api import WormsAPI, is_fish, is_true_value, matches_habitat


def worms_record(aphia_id=1, name="Cyprinus carpio", taxon_class="Teleostei",
                 status="accepted", marine=0, freshwater=1, brackish=0,
                 family="Cyprinidae"):
    """สร้าง record หน้าตาเหมือนที่ WoRMS ส่งกลับมาจริง"""
    return {
        "AphiaID": aphia_id,
        "scientificname": name,
        "class": taxon_class,
        "family": family,
        "status": status,
        "isMarine": marine,
        "isFreshwater": freshwater,
        "isBrackish": brackish,
    }


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
        self.calls = []

    def get(self, url, params=None, headers=None, timeout=None):
        self.calls.append((url, params))
        if self.error:
            raise self.error
        return self.response


def make_api(response=None, error=None, words=("carp",)):
    return WormsAPI(http=FakeHttp(response, error), search_words=words)


class TestValueHelpers:
    @pytest.mark.parametrize("value", [True, 1, "1", "true", "YES", " y "])
    def test_recognises_true_forms(self, value):
        """WoRMS ส่งค่ามาได้หลายรูปแบบ ต้องแปลงเป็น True ได้ทั้งหมด"""
        assert is_true_value(value) is True

    @pytest.mark.parametrize("value", [False, 0, "0", "false", None, ""])
    def test_recognises_false_forms(self, value):
        assert is_true_value(value) is False


class TestFishFilter:
    def test_accepts_known_fish_class(self):
        assert is_fish(worms_record(taxon_class="Teleostei")) is True

    def test_rejects_non_fish_class(self):
        """'Fisherana' เป็นหนอนทะเล ไม่ใช่ปลา ต้องถูกกรองทิ้ง"""
        assert is_fish(worms_record(taxon_class="Sipuncula")) is False

    def test_rejects_record_without_class(self):
        assert is_fish({"scientificname": "Unknown"}) is False


class TestHabitatMatching:
    def test_matches_freshwater(self):
        assert matches_habitat(worms_record(freshwater=1), FRESHWATER) is True

    def test_matches_marine(self):
        assert matches_habitat(worms_record(marine=1), MARINE) is True

    def test_matches_brackish(self):
        assert matches_habitat(worms_record(brackish=1), BRACKISH) is True

    def test_does_not_match_other_habitat(self):
        assert matches_habitat(worms_record(freshwater=1, marine=0), MARINE) is False

    def test_unknown_location_never_matches(self):
        assert matches_habitat(worms_record(), "lava") is False


class TestSearchByVernacular:
    def test_calls_vernacular_endpoint_with_like(self):
        """ต้องยิงที่ AphiaRecordsByVernacular ไม่ใช่ AphiaRecordsByName"""
        http = FakeHttp(FakeResponse([worms_record()]))
        WormsAPI(http=http).search_by_vernacular("carp")
        url, params = http.calls[0]
        assert "AphiaRecordsByVernacular/carp" in url
        assert params == {"like": "true"}

    @pytest.mark.parametrize("status_code", [204, 404])
    def test_treats_empty_status_as_no_result(self, status_code):
        """WoRMS ตอบ 204 เมื่อค้นไม่เจอ ต้องไม่ถือเป็นข้อผิดพลาด"""
        api = make_api(FakeResponse(status_code=status_code))
        assert api.search_by_vernacular("carp") == []

    def test_returns_empty_list_when_payload_is_not_a_list(self):
        api = make_api(FakeResponse({"error": "nope"}))
        assert api.search_by_vernacular("carp") == []


class TestFetchFishRecords:
    def test_collects_accepted_fish(self):
        api = make_api(FakeResponse([worms_record()]))
        records = api.fetch_fish_records()
        assert len(records) == 1
        assert api.last_error is None

    def test_skips_unaccepted_status(self):
        api = make_api(FakeResponse([worms_record(status="unaccepted")]))
        assert api.fetch_fish_records() == {}

    def test_skips_non_fish_records(self):
        api = make_api(FakeResponse([worms_record(taxon_class="Sipuncula")]))
        assert api.fetch_fish_records() == {}

    def test_does_not_duplicate_same_aphia_id(self):
        api = make_api(FakeResponse([worms_record(), worms_record()]),
                       words=("carp", "perch"))
        assert len(api.fetch_fish_records()) == 1

    def test_records_error_when_connection_fails(self):
        api = make_api(error=requests.exceptions.ConnectionError("ปิดอยู่"))
        assert api.fetch_fish_records() == {}
        assert "ConnectionError" in api.last_error

    def test_records_error_on_timeout(self):
        api = make_api(error=requests.exceptions.Timeout("ช้า"))
        api.fetch_fish_records()
        assert "Timeout" in api.last_error

    def test_records_error_on_http_error(self):
        api = make_api(FakeResponse(status_code=500))
        api.fetch_fish_records()
        assert "HTTPError" in api.last_error

    def test_records_error_when_body_is_not_json(self):
        api = make_api(FakeResponse(payload=None))
        api.fetch_fish_records()
        assert "JSON" in api.last_error
