"""ตัวเชื่อมต่อ Open Fisheries API (Sprint 2 — Back-End)

Open Fisheries เป็นฐานข้อมูลการประมงที่เปิดให้ใช้ฟรี ในโครงการนี้ใช้เป็นแหล่ง
**ชื่อสามัญภาษาอังกฤษ** ของปลา ซึ่งเป็นสิ่งที่ WoRMS ไม่ได้ให้มาในผลการค้นหา

ผลลัพธ์คือ dict ที่จับคู่ ชื่อวิทยาศาสตร์ (ตัวพิมพ์เล็ก) → ชื่อสามัญ
เอาไว้ให้ `FishAPI` นำไปเติมชื่อที่อ่านง่ายให้ปลาที่ได้จาก WoRMS
"""

import requests

SPECIES_URL = "https://www.openfisheries.org/api/landings/species.json"
DEFAULT_TIMEOUT = 40
USER_AGENT = "how-do-you-fish/1.0 (CP352301 Script Programming)"


class OpenFisheriesAPI:
    """ดึงตารางชื่อสามัญของสัตว์น้ำจาก Open Fisheries"""

    def __init__(self, url=SPECIES_URL, timeout=DEFAULT_TIMEOUT, http=None):
        self.url = url
        self.timeout = timeout
        self.http = http or requests
        self.last_error = None
        self._names = None

    def fetch_common_names(self):
        """คืน dict ชื่อวิทยาศาสตร์ (lowercase) → ชื่อสามัญ

        ถ้าเรียกไม่สำเร็จจะคืน dict ว่าง ซึ่งแปลว่าเกมจะใช้ชื่อวิทยาศาสตร์แทน
        ไม่ถือเป็นข้อผิดพลาดร้ายแรง เพราะเป็นข้อมูลเสริม ไม่ใช่ข้อมูลหลัก
        """
        if self._names is not None:
            return self._names

        try:
            response = self.http.get(
                self.url,
                headers={"Accept": "application/json", "User-Agent": USER_AGENT},
                timeout=self.timeout,
            )
            response.raise_for_status()
            records = response.json()
        except requests.exceptions.RequestException as error:
            self.last_error = f"เชื่อมต่อ Open Fisheries ไม่ได้: {type(error).__name__}"
            self._names = {}
            return self._names
        except ValueError:
            self.last_error = "ข้อมูลจาก Open Fisheries ไม่ใช่ JSON ที่ถูกต้อง"
            self._names = {}
            return self._names

        if not isinstance(records, list):
            self.last_error = "รูปแบบข้อมูลจาก Open Fisheries ไม่ใช่ JSON Array"
            self._names = {}
            return self._names

        names = {}
        for record in records:
            scientific = str(record.get("scientific_name") or "").strip().lower()
            english = str(record.get("english_name") or "").strip()
            if scientific and english:
                names[scientific] = english

        self.last_error = None
        self._names = names
        return self._names
