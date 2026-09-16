"""Unit tests ของตัวประสานข้อมูลปลาสอง API (Sprint 2)

`FishAPI` รวมผลจาก WoRMS (แหล่งน้ำ) เข้ากับ Open Fisheries (ชื่อสามัญ)
เทสต์ชุดนี้ใช้ตัวปลอมแทน API ทั้งสองตัว จึงไม่ยิงเครือข่ายจริงเลย
"""

import pytest

from src.fish import BRACKISH, FRESHWATER, MARINE
from src.fish_api import FishAPI, build_entry


def worms_record(aphia_id=1, name="Carassius auratus", freshwater=1, marine=0,
                 brackish=0, family="Cyprinidae"):
    return {
        "AphiaID": aphia_id,
        "scientificname": name,
        "class": "Teleostei",
        "family": family,
        "status": "accepted",
        "isFreshwater": freshwater,
        "isMarine": marine,
        "isBrackish": brackish,
    }


class FakeWorms:
    """ตัวแทนของ WormsAPI"""

    def __init__(self, records=None, error=None):
        self.records = records if records is not None else {}
        self.last_error = error
        self.calls = 0

    def fetch_fish_records(self):
        self.calls += 1
        return self.records


class FakeOpenFisheries:
    """ตัวแทนของ OpenFisheriesAPI"""

    def __init__(self, names=None, error=None):
        self.names = names or {}
        self.last_error = error
        self.calls = 0

    def fetch_common_names(self):
        self.calls += 1
        return self.names


COMMON_NAMES = {"carassius auratus": "Goldfish"}


class TestBuildEntry:
    def test_uses_common_name_when_available(self):
        entry = build_entry(worms_record(), FRESHWATER, COMMON_NAMES)
        assert entry["name"] == "Goldfish"
        assert entry["scientific_name"] == "Carassius auratus"

    def test_falls_back_to_scientific_name(self):
        entry = build_entry(worms_record(), FRESHWATER, {})
        assert entry["name"] == "Carassius auratus"

    def test_match_is_case_insensitive(self):
        entry = build_entry(worms_record(name="CARASSIUS AURATUS"),
                            FRESHWATER, COMMON_NAMES)
        assert entry["name"] == "Goldfish"

    def test_keeps_taxonomy_in_description(self):
        entry = build_entry(worms_record(), FRESHWATER, COMMON_NAMES)
        assert "Carassius auratus" in entry["description"]
        assert "Cyprinidae" in entry["description"]

    def test_fills_missing_fields(self):
        entry = build_entry({"AphiaID": 9}, MARINE, {})
        assert entry["name"] == "ปลาปริศนา"
        assert "ไม่ระบุ" in entry["description"]


class TestFetchSpecies:
    def test_merges_both_apis(self):
        api = FishAPI(worms=FakeWorms({1: worms_record()}),
                      openfisheries=FakeOpenFisheries(COMMON_NAMES))
        species = api.fetch_species(FRESHWATER)
        assert [item["name"] for item in species] == ["Goldfish"]
        assert api.using_fallback is False
        assert api.enriched_count == 1

    def test_filters_by_habitat(self):
        records = {
            1: worms_record(1, "Carassius auratus", freshwater=1, marine=0),
            2: worms_record(2, "Thunnus albacares", freshwater=0, marine=1),
        }
        api = FishAPI(worms=FakeWorms(records),
                      openfisheries=FakeOpenFisheries())
        assert len(api.fetch_species(FRESHWATER)) == 1
        assert len(api.fetch_species(MARINE)) == 1

    def test_calls_worms_once_for_every_location(self):
        """ดึงจาก WoRMS ครั้งเดียวแล้วแยกแหล่งน้ำเอง ไม่ยิงซ้ำสามรอบ"""
        worms = FakeWorms({1: worms_record(brackish=1, freshwater=1, marine=1)})
        api = FishAPI(worms=worms, openfisheries=FakeOpenFisheries())
        api.fetch_species(FRESHWATER)
        api.fetch_species(MARINE)
        api.fetch_species(BRACKISH)
        assert worms.calls == 1

    def test_caches_result_per_location(self):
        openfish = FakeOpenFisheries(COMMON_NAMES)
        api = FishAPI(worms=FakeWorms({1: worms_record()}), openfisheries=openfish)
        api.fetch_species(FRESHWATER)
        api.fetch_species(FRESHWATER)
        assert openfish.calls == 1

    def test_still_works_when_common_names_unavailable(self):
        """Open Fisheries ล่มต้องไม่ทำให้เกมพัง แค่ใช้ชื่อวิทยาศาสตร์แทน"""
        api = FishAPI(worms=FakeWorms({1: worms_record()}),
                      openfisheries=FakeOpenFisheries({}, error="ล่ม"))
        species = api.fetch_species(FRESHWATER)
        assert species[0]["name"] == "Carassius auratus"
        assert api.using_fallback is False
        assert api.enriched_count == 0


class TestFallback:
    def test_falls_back_when_worms_returns_nothing(self):
        api = FishAPI(worms=FakeWorms({}, error="เชื่อมต่อ WoRMS ไม่ได้: ConnectionError"),
                      openfisheries=FakeOpenFisheries())
        species = api.fetch_species(FRESHWATER)
        assert api.using_fallback is True
        assert "ConnectionError" in api.last_error
        assert species and all(item["location"] == FRESHWATER for item in species)

    def test_falls_back_when_no_fish_in_that_habitat(self):
        api = FishAPI(worms=FakeWorms({1: worms_record(freshwater=1, brackish=0)}),
                      openfisheries=FakeOpenFisheries())
        api.fetch_species(BRACKISH)
        assert api.using_fallback is True

    @pytest.mark.parametrize("location", [FRESHWATER, MARINE, BRACKISH])
    def test_local_data_covers_every_habitat(self, location):
        species = FishAPI.local_species(location)
        assert species
        assert all(item["location"] == location for item in species)


class TestRandomSpecies:
    def test_picks_from_returned_list(self):
        api = FishAPI(worms=FakeWorms({1: worms_record()}),
                      openfisheries=FakeOpenFisheries(COMMON_NAMES))
        assert api.random_species(FRESHWATER)["name"] == "Goldfish"
