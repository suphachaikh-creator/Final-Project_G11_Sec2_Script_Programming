"""ชั้นเชื่อมต่อข้อมูลปลา — รวมสอง Public API เข้าด้วยกัน (Sprint 2 — Back-End)

โครงการใช้ Public API สองตัวที่เติมเต็มกัน

- **WoRMS** — ให้แหล่งที่อยู่ (น้ำจืด / น้ำเค็ม / น้ำกร่อย) และข้อมูลอนุกรมวิธาน
  เป็น API เดียวที่บอกแหล่งน้ำได้ จึงใช้แยกสถานที่ตกปลาของเกม
- **Open Fisheries** — ให้ชื่อสามัญภาษาอังกฤษ ทำให้ผู้เล่นเห็น "Goldfish"
  แทนชื่อวิทยาศาสตร์ที่จำยาก

คลาสนี้ทำหน้าที่ประสานทั้งสองตัว จับคู่ด้วยชื่อวิทยาศาสตร์ แล้วแคชผลไว้ต่อหนึ่งแหล่งน้ำ
ถ้าเชื่อมต่อไม่ได้เลย จะสลับไปใช้ไฟล์ข้อมูลสำรองในเครื่องโดยอัตโนมัติ
"""

import json
import os
import random

from src.fish import BRACKISH, FRESHWATER, MARINE
from src.openfisheries_api import OpenFisheriesAPI
from src.worms_api import WormsAPI, matches_habitat

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
SPECIES_FILE = os.path.join(DATA_DIR, "fish_species.json")

BUILTIN_SPECIES = [
    {"name": "Goldfish", "scientific_name": "Carassius auratus", "location": FRESHWATER,
     "family": "Cyprinidae", "description": "ชื่อวิทยาศาสตร์ Carassius auratus · วงศ์ Cyprinidae"},
    {"name": "Nile tilapia", "scientific_name": "Oreochromis niloticus",
     "location": FRESHWATER, "family": "Cichlidae",
     "description": "ชื่อวิทยาศาสตร์ Oreochromis niloticus · วงศ์ Cichlidae"},
    {"name": "Yellowfin tuna", "scientific_name": "Thunnus albacares", "location": MARINE,
     "family": "Scombridae", "description": "ชื่อวิทยาศาสตร์ Thunnus albacares · วงศ์ Scombridae"},
    {"name": "Atlantic mackerel", "scientific_name": "Scomber scombrus", "location": MARINE,
     "family": "Scombridae", "description": "ชื่อวิทยาศาสตร์ Scomber scombrus · วงศ์ Scombridae"},
    {"name": "Barramundi", "scientific_name": "Lates calcarifer", "location": BRACKISH,
     "family": "Latidae", "description": "ชื่อวิทยาศาสตร์ Lates calcarifer · วงศ์ Latidae"},
    {"name": "Flathead grey mullet", "scientific_name": "Mugil cephalus",
     "location": BRACKISH, "family": "Mugilidae",
     "description": "ชื่อวิทยาศาสตร์ Mugil cephalus · วงศ์ Mugilidae"},
]


def build_entry(record, location, common_names=None):
    """แปลง record ของ WoRMS เป็นรูปแบบที่เกมใช้ พร้อมเติมชื่อสามัญจาก Open Fisheries"""
    scientific = record.get("scientificname") or "ปลาปริศนา"
    family = record.get("family") or "ไม่ระบุ"
    english = (common_names or {}).get(scientific.strip().lower())

    return {
        "name": english or scientific,
        "scientific_name": scientific,
        "location": location,
        "family": family,
        "aphia_id": record.get("AphiaID"),
        "description": f"ชื่อวิทยาศาสตร์ {scientific} · วงศ์ {family}",
    }


class FishAPI:
    """ตัวประสานข้อมูลปลาจาก WoRMS และ Open Fisheries พร้อมระบบสำรอง"""

    def __init__(self, worms=None, openfisheries=None):
        self.worms = worms or WormsAPI()
        self.openfisheries = openfisheries or OpenFisheriesAPI()
        self.last_error = None
        self.using_fallback = False
        self.enriched_count = 0
        self._cache = {}
        self._records = None

    def _load_records(self):
        """ดึง record ปลาจาก WoRMS ครั้งเดียวแล้วเก็บไว้ใช้กับทุกแหล่งน้ำ"""
        if self._records is None:
            self._records = self.worms.fetch_fish_records()
        return self._records

    def fetch_species(self, location):
        """ดึงชนิดปลาของแหล่งน้ำที่เลือก คืนค่า list ของ dict

        ผลลัพธ์ถูกแคชไว้ต่อหนึ่งแหล่งน้ำ จึงยิง API แค่ครั้งแรกของแต่ละสถานที่
        """
        if location in self._cache:
            return self._cache[location]

        records = self._load_records()
        matched = [record for record in records.values()
                   if matches_habitat(record, location)]

        if not matched:
            self.last_error = self.worms.last_error or "WoRMS ไม่พบปลาของแหล่งน้ำนี้"
            self.using_fallback = True
            self._cache[location] = self.local_species(location)
            return self._cache[location]

        common_names = self.openfisheries.fetch_common_names()
        entries = [build_entry(record, location, common_names) for record in matched]
        self.enriched_count = sum(
            1 for entry in entries if entry["name"] != entry["scientific_name"]
        )

        self.last_error = self.openfisheries.last_error
        self.using_fallback = False
        self._cache[location] = entries
        return entries

    # ------------------------------------------------------------- fallback
    @staticmethod
    def local_species(location):
        """อ่านข้อมูลปลาสำรองจากไฟล์ในเครื่อง ถ้าไฟล์หายจะใช้ชุดที่ฝังไว้ในโค้ด"""
        species = BUILTIN_SPECIES
        if os.path.exists(SPECIES_FILE):
            try:
                with open(SPECIES_FILE, encoding="utf-8") as handle:
                    loaded = json.load(handle)
                if isinstance(loaded, list) and loaded:
                    species = loaded
            except (json.JSONDecodeError, OSError):
                species = BUILTIN_SPECIES

        filtered = [item for item in species if item.get("location") == location]
        return filtered or [item for item in BUILTIN_SPECIES
                            if item.get("location") == location]

    def random_species(self, location, rng=None):
        """สุ่มปลาหนึ่งชนิดจากแหล่งน้ำที่เลือก"""
        generator = rng or random
        species = self.fetch_species(location)
        if not species:
            return {"name": "ปลาปริศนา", "location": location, "description": ""}
        return generator.choice(species)
