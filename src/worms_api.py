"""ตัวเชื่อมต่อ WoRMS API (Sprint 2 — Back-End)

WoRMS (World Register of Marine Species) เป็นฐานข้อมูลสิ่งมีชีวิตทางน้ำระดับโลก
ในโครงการนี้ใช้ WoRMS เป็นแหล่ง **แหล่งที่อยู่และข้อมูลอนุกรมวิธาน** ของปลา
เพราะเป็น API เดียวที่บอกได้ว่าปลาชนิดนั้นอยู่ในน้ำจืด น้ำเค็ม หรือน้ำกร่อย
"""

import requests

from src.fish import BRACKISH, FRESHWATER, MARINE

BASE_URL = "https://www.marinespecies.org/rest"
DEFAULT_TIMEOUT = 20
USER_AGENT = "how-do-you-fish/1.0 (CP352301 Script Programming)"

# ชั้นทางอนุกรมวิธานที่นับว่าเป็นปลา ใช้กรองผลลัพธ์ที่ WoRMS ส่งกลับมา
FISH_CLASSES = {
    "Actinopterygii", "Actinopteri", "Elasmobranchii", "Holocephali", "Myxini",
    "Petromyzonti", "Cephalaspidomorphi", "Chondrichthyes", "Cladistii",
    "Sarcopterygii", "Coelacanthi", "Dipneusti", "Teleostei", "Chondrostei",
}

# ฟิลด์ของ WoRMS ที่บอกว่าชนิดนั้นอยู่ในแหล่งน้ำใด
HABITAT_FIELD = {
    FRESHWATER: "isFreshwater",
    MARINE: "isMarine",
    BRACKISH: "isBrackish",
}

# คำค้นชื่อสามัญ เลือกให้ครอบคลุมทั้งสามแหล่งน้ำ
SEARCH_WORDS = ("carp", "catfish", "perch", "tilapia", "goby",
                "snapper", "grouper", "mackerel", "herring", "shark")


def is_true_value(value):
    """WoRMS ส่งค่าฟิลด์ habitat มาได้ทั้ง 1, "1", True หรือ None จึงต้องแปลงให้เป็น bool"""
    if value is True:
        return True
    if isinstance(value, int):
        return value == 1
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y"}
    return False


def is_fish(record):
    """ตรวจว่า record ที่ได้เป็นปลาจริง ไม่ใช่สัตว์กลุ่มอื่นที่ชื่อพ้องกัน"""
    return str(record.get("class") or "").strip() in FISH_CLASSES


def matches_habitat(record, location):
    """ตรวจว่าชนิดนี้อยู่ในแหล่งน้ำที่ผู้เล่นเลือกหรือไม่"""
    field = HABITAT_FIELD.get(location)
    return bool(field) and is_true_value(record.get(field))


class WormsAPI:
    """เรียก WoRMS เพื่อหาชนิดปลาพร้อมข้อมูลแหล่งที่อยู่"""

    def __init__(self, base_url=BASE_URL, timeout=DEFAULT_TIMEOUT, http=None,
                 search_words=SEARCH_WORDS):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.http = http or requests
        self.search_words = tuple(search_words)
        self.last_error = None

    def search_by_vernacular(self, word):
        """ค้นชนิดปลาจาก **ชื่อสามัญ** — endpoint นี้คือตัวที่ค้นเจอปลาจริง

        endpoint `AphiaRecordsByName` ค้นจากชื่อวิทยาศาสตร์ คำอย่าง "fish" หรือ "shark"
        จึงไปตรงกับสกุลของสัตว์กลุ่มอื่นที่สะกดคล้ายกันแทน และได้ปลากลับมาเป็นศูนย์
        """
        response = self.http.get(
            f"{self.base_url}/AphiaRecordsByVernacular/{word}",
            params={"like": "true"},
            headers={"Accept": "application/json", "User-Agent": USER_AGENT},
            timeout=self.timeout,
        )

        # WoRMS ตอบ 204 เมื่อค้นไม่เจอ ซึ่งไม่ใช่ข้อผิดพลาด
        if response.status_code in (204, 404):
            return []

        response.raise_for_status()
        data = response.json()
        return data if isinstance(data, list) else []

    def fetch_fish_records(self):
        """รวบรวม record ของปลาที่สถานะ accepted จากทุกคำค้น คืนค่า dict ที่คีย์เป็น AphiaID"""
        collected = {}
        self.last_error = None

        for word in self.search_words:
            try:
                records = self.search_by_vernacular(word)
            except requests.exceptions.RequestException as error:
                self.last_error = f"เชื่อมต่อ WoRMS ไม่ได้: {type(error).__name__}"
                break
            except ValueError:
                self.last_error = "ข้อมูลจาก WoRMS ไม่ใช่ JSON ที่ถูกต้อง"
                break

            for record in records:
                aphia_id = record.get("AphiaID")
                if not aphia_id or aphia_id in collected:
                    continue
                if record.get("status") != "accepted" or not is_fish(record):
                    continue
                collected[aphia_id] = record

        return collected
