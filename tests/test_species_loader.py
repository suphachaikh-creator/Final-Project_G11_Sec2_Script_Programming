"""Unit tests ของตัวโหลดข้อมูลปลาเบื้องหลัง (Sprint 3)

เทสต์ชุดนี้ **ไม่สร้างเธรดจริง** เพราะฉีดตัวสร้างเธรดเข้ามาได้ทาง `spawn`
จึงสั่งให้ทำงานตามลำดับที่ต้องการได้ ไม่มีเคสไหนต้องรอเวลาจริงหรือยิงเครือข่าย

ประเด็นหลักคือ **การสุ่มปลาต้องไม่รอเครือข่ายเด็ดขาด** เพราะถ้ารอ
หน้าต่างจะค้างราว 34 วินาทีตอนผู้เล่นจับปลาตัวแรก
"""

import pytest

from src.fish import BRACKISH, FRESHWATER, MARINE
from src.gui.species_loader import (LOADING, OFFLINE, ONLINE, SpeciesLoader)

ONLINE_FISH = {"name": "Atlantic salmon", "location": FRESHWATER}
LOCAL_FISH = [{"name": "ปลาสำรอง", "location": FRESHWATER}]


class FakeApi:
    """ตัวแทนของ FishAPI ที่นับว่าถูกเรียกไปกี่ครั้ง"""

    def __init__(self, error=None, using_fallback=False):
        self.error = error
        self.using_fallback = using_fallback
        self.fetched = []

    def fetch_species(self, location):
        self.fetched.append(location)
        if self.error:
            raise self.error
        return [ONLINE_FISH]

    def random_species(self, location, rng=None):
        return ONLINE_FISH

    @staticmethod
    def local_species(location):
        return LOCAL_FISH


class ManualSpawn:
    """เก็บงานไว้ก่อน แล้วให้เทสต์สั่งรันเองเมื่อพร้อม"""

    def __init__(self):
        self.jobs = []

    def __call__(self, work):
        self.jobs.append(work)

    def run(self):
        for job in self.jobs:
            job()
        self.jobs = []


def make_loader(api=None, spawn=None):
    return SpeciesLoader(api=api or FakeApi(), spawn=spawn or ManualSpawn())


class TestStart:
    def test_nothing_is_fetched_before_start(self):
        api = FakeApi()
        make_loader(api)
        assert api.fetched == []

    def test_start_hands_the_work_to_the_spawner(self):
        spawn = ManualSpawn()
        make_loader(spawn=spawn).start()
        assert len(spawn.jobs) == 1

    def test_start_twice_only_runs_once(self):
        spawn = ManualSpawn()
        loader = make_loader(spawn=spawn)
        assert loader.start() is True
        assert loader.start() is False
        assert len(spawn.jobs) == 1

    def test_every_location_is_loaded(self):
        api = FakeApi()
        spawn = ManualSpawn()
        make_loader(api, spawn).start()
        spawn.run()
        assert set(api.fetched) == {FRESHWATER, MARINE, BRACKISH}


class TestNeverBlocks:
    """หัวใจของไฟล์นี้ — จับปลาได้ต้องไม่รอเครือข่าย"""

    def test_uses_local_data_before_loading_finishes(self):
        api = FakeApi()
        loader = make_loader(api)
        species = loader.random_species(FRESHWATER)
        assert species == LOCAL_FISH[0]
        assert api.fetched == [], "ต้องไม่ยิงเครือข่ายตอนผู้เล่นจับปลา"

    def test_uses_online_data_after_loading_finishes(self):
        spawn = ManualSpawn()
        loader = make_loader(spawn=spawn)
        loader.start()
        spawn.run()
        assert loader.random_species(FRESHWATER) == ONLINE_FISH

    def test_a_location_that_finished_does_not_wait_for_the_others(self):
        """โหลดน้ำจืดเสร็จแล้วต้องใช้ข้อมูลจริงได้ทันที ไม่ต้องรอครบสามแหล่ง"""
        loader = make_loader()
        loader._load_one(FRESHWATER)
        assert loader.is_ready(FRESHWATER) is True
        assert loader.is_ready(MARINE) is False
        assert loader.random_species(FRESHWATER) == ONLINE_FISH
        assert loader.random_species(MARINE) == LOCAL_FISH[0]

    def test_failure_still_marks_the_location_as_done(self):
        """โหลดพังต้องไม่ค้างสถานะ 'กำลังโหลด' ตลอดไป"""
        loader = make_loader(FakeApi(error=ConnectionError("เน็ตหลุด")))
        loader._load_one(FRESHWATER)
        assert loader.is_ready(FRESHWATER) is True
        assert "ConnectionError" in loader.last_error

    def test_still_returns_a_fish_when_there_is_no_local_data(self):
        class EmptyApi(FakeApi):
            @staticmethod
            def local_species(location):
                return []

        species = make_loader(EmptyApi()).random_species(FRESHWATER)
        assert species["name"] == "ปลาปริศนา"


class TestStatus:
    def test_loading_until_every_location_is_done(self):
        loader = make_loader()
        assert loader.status() == LOADING
        loader._load_one(FRESHWATER)
        assert loader.status() == LOADING

    def test_online_when_the_api_worked(self):
        spawn = ManualSpawn()
        loader = make_loader(spawn=spawn)
        loader.start()
        spawn.run()
        assert loader.status() == ONLINE
        assert loader.using_fallback is False

    def test_offline_when_the_api_used_local_data(self):
        spawn = ManualSpawn()
        loader = make_loader(FakeApi(using_fallback=True), spawn)
        loader.start()
        spawn.run()
        assert loader.status() == OFFLINE
        assert loader.using_fallback is True

    def test_counts_as_fallback_while_still_loading(self):
        """ยังโหลดไม่เสร็จก็ถือว่าใช้ข้อมูลสำรองอยู่ เพราะตอนนั้นใช้ของในเครื่องจริงๆ"""
        assert make_loader().using_fallback is True

    @pytest.mark.parametrize("state,words", [
        (LOADING, "กำลังโหลด"), (ONLINE, "ออนไลน์"), (OFFLINE, "ออฟไลน์")])
    def test_status_text_is_readable(self, state, words):
        from src.gui.species_loader import STATUS_TEXT
        assert words in STATUS_TEXT[state]

    def test_is_complete_after_every_location(self):
        loader = make_loader()
        for location in (FRESHWATER, MARINE, BRACKISH):
            loader._load_one(location)
        assert loader.is_complete is True
