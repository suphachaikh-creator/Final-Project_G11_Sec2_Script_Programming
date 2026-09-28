"""โหลดข้อมูลชนิดปลาไว้ล่วงหน้าโดยไม่ให้หน้าต่างค้าง (Sprint 3 — Full-Stack)

**ปัญหาที่ไฟล์นี้แก้**

`FishAPI.random_species()` ยิง WoRMS กับ Open Fisheries จริงในครั้งแรกที่ถูกเรียก
ซึ่งวัดได้ว่าใช้เวลาราว **34 วินาที** ถ้าเรียกตรงๆ ตอนผู้เล่นจับปลาได้
Tkinter จะหยุดตอบสนองทั้งหน้าต่างตลอดเวลานั้น เพราะทุกอย่างอยู่บนเธรดเดียวกัน

**วิธีแก้** มีสองชั้น

1. เริ่มโหลดทันทีที่เปิดเกมในเธรดเบื้องหลัง ระหว่างนั้นผู้เล่นเดินเมนูได้ตามปกติ
2. `random_species()` ของไฟล์นี้ **ไม่รอเน็ตเด็ดขาด** ถ้ายังโหลดไม่เสร็จจะหยิบจาก
   ข้อมูลสำรองในเครื่องให้ทันที ผู้เล่นจึงเล่นต่อได้เลยแม้เพิ่งเปิดเกมมาไม่กี่วินาที

ตัวสร้างเธรดฉีดเข้ามาได้ทาง `spawn` เทสต์จึงสั่งให้ทำงานแบบตรงไปตรงมาได้
โดยไม่ต้องสร้างเธรดจริงและไม่ต้องรอ
"""

import random
import threading

from src.fish import LOCATIONS
from src.fish_api import FishAPI

LOADING = "loading"
ONLINE = "online"
OFFLINE = "offline"

STATUS_TEXT = {
    LOADING: "กำลังโหลดข้อมูลปลาจากอินเทอร์เน็ต · ระหว่างนี้ใช้ข้อมูลสำรองในเครื่อง",
    ONLINE: "ออนไลน์ — ข้อมูลปลาจาก WoRMS + Open Fisheries",
    OFFLINE: "ออฟไลน์ — ใช้ข้อมูลปลาสำรองในเครื่อง",
}


def spawn_thread(work):
    """เริ่มงานในเธรดเบื้องหลังที่ไม่กันโปรแกรมปิด"""
    thread = threading.Thread(target=work, daemon=True)
    thread.start()
    return thread


class SpeciesLoader:
    """ห่อ `FishAPI` ไว้อีกชั้น ให้เรียกใช้ได้โดยไม่ทำให้หน้าต่างค้าง

    มีหน้าตาเหมือน `FishAPI` ตรงที่มี `random_species()` และ `using_fallback`
    จึงส่งเข้าไปแทนกันได้เลยโดยไม่ต้องแก้ `presenter.py`
    """

    def __init__(self, api=None, locations=LOCATIONS, spawn=None):
        self.api = api or FishAPI()
        self.locations = tuple(locations)
        self.spawn = spawn or spawn_thread
        self.ready = set()
        self.started = False
        self.last_error = None
        self._lock = threading.Lock()

    # --------------------------------------------------------------- สถานะ
    @property
    def using_fallback(self):
        """ตอนนี้กำลังใช้ข้อมูลสำรองอยู่หรือไม่"""
        if not self.is_complete:
            return True
        return bool(getattr(self.api, "using_fallback", False))

    @property
    def is_complete(self):
        """โหลดครบทุกแหล่งน้ำแล้วหรือยัง"""
        with self._lock:
            return len(self.ready) >= len(self.locations)

    def is_ready(self, location):
        """แหล่งน้ำนี้พร้อมใช้ข้อมูลจริงหรือยัง"""
        with self._lock:
            return location in self.ready

    def status(self):
        """สถานะปัจจุบัน — กำลังโหลด · ออนไลน์ · ออฟไลน์"""
        if not self.is_complete:
            return LOADING
        return OFFLINE if self.using_fallback else ONLINE

    def status_text(self):
        """ข้อความสถานะสำหรับแสดงบนหน้าจอ"""
        return STATUS_TEXT[self.status()]

    # ---------------------------------------------------------- การโหลดล่วงหน้า
    def start(self):
        """เริ่มโหลดเบื้องหลัง เรียกซ้ำไม่มีผล"""
        if self.started:
            return False
        self.started = True
        self.spawn(self._load_all)
        return True

    def _load_all(self):
        """งานที่รันในเธรดเบื้องหลัง"""
        for location in self.locations:
            self._load_one(location)

    def _load_one(self, location):
        """โหลดแหล่งน้ำเดียว ล้มเหลวก็ต้องทำเครื่องหมายว่าเสร็จ

        ถ้าไม่ทำเครื่องหมาย แหล่งน้ำนั้นจะค้างสถานะ 'กำลังโหลด' ตลอดไป
        """
        try:
            self.api.fetch_species(location)
        except Exception as error:  # noqa: BLE001 - เครือข่ายล้มได้หลายแบบ
            self.last_error = f"โหลด {location} ไม่สำเร็จ: {type(error).__name__}"
        finally:
            with self._lock:
                self.ready.add(location)

    # ------------------------------------------------------------ การสุ่มปลา
    def random_species(self, location, rng=None):
        """สุ่มปลาหนึ่งชนิด **โดยไม่รอเครือข่ายเด็ดขาด**

        พร้อมแล้วใช้ข้อมูลจริง ยังไม่พร้อมใช้ข้อมูลสำรองในเครื่องไปก่อน
        """
        if self.is_ready(location):
            return self.api.random_species(location, rng=rng)

        generator = rng or random
        species = self.api.local_species(location)
        if not species:
            return {"name": "ปลาปริศนา", "location": location, "description": ""}
        return generator.choice(species)
