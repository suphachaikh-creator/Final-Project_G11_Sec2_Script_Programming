"""ตรวจว่ามีเกมเวอร์ชันใหม่บน GitHub Releases หรือไม่ (Final Sprint)

เป็นครึ่งหนึ่งของ CD — อีกครึ่งคือ `.github/workflows/release.yml` ที่สร้าง release ให้เอง
ทุกครั้งที่ push tag เช่น `v1.0.1` ไฟล์นี้แค่ **แจ้ง** ผู้เล่นว่ามีเวอร์ชันใหม่และดาวน์โหลดได้ที่ไหน
ไม่ดาวน์โหลดหรือเขียนทับไฟล์ของเกมเอง

เป็นของเสริมเหมือน Open Fisheries และ Gemini — ไม่มีอินเทอร์เน็ต ยังไม่มี release
หรือ GitHub ตอบผิดรูปแบบ เกมต้องเล่นได้ตามปกติ `check()` จึงไม่โยน exception
"""

import threading

import requests

from src import __version__

REPO = "suphachaikh-creator/Final-Project_G11_Sec2_Script_Programming"
LATEST_RELEASE_API = f"https://api.github.com/repos/{REPO}/releases/latest"
RELEASES_PAGE = f"https://github.com/{REPO}/releases/latest"
TIMEOUT = 5

CHECKING = "checking"
LATEST = "latest"
AVAILABLE = "available"
UNKNOWN = "unknown"


def parse_version(text):
    """แปลง `"v1.2.3"` หรือ `"1.2.3"` เป็น `(1, 2, 3)` คืน None ถ้ารูปแบบไม่ถูกต้อง"""
    if not isinstance(text, str):
        return None
    parts = text.strip().lstrip("vV").split(".")
    if len(parts) != 3 or not all(part.isdecimal() for part in parts):
        return None
    return tuple(int(part) for part in parts)


def spawn_thread(work):
    """รันงานในเธรดเบื้องหลัง ไม่ให้หน้าต่างค้างระหว่างรอ GitHub"""
    thread = threading.Thread(target=work, daemon=True)
    thread.start()
    return thread


class UpdateChecker:
    """ถาม GitHub ว่า release ล่าสุดคือเวอร์ชันไหน แล้วเทียบกับเวอร์ชันที่เล่นอยู่

    ฉีด `http` และ `spawn` เข้ามาได้เหมือน `WormsAPI` กับ `SpeciesLoader`
    เทสต์จึงไม่ยิงเครือข่ายจริงและไม่สร้างเธรดจริง
    """

    def __init__(self, current=__version__, http=None, spawn=None):
        self.current = current
        self.http = http or requests
        self.spawn = spawn or spawn_thread
        self.status = None
        self.latest = None
        self.url = RELEASES_PAGE
        self.last_error = None

    def start(self):
        """เริ่มตรวจในเบื้องหลัง เรียกซ้ำได้โดยไม่ยิงซ้ำ"""
        if self.status is not None:
            return
        self.status = CHECKING
        self.spawn(self.check)

    @property
    def is_complete(self):
        """ตรวจเสร็จแล้วหรือยัง (ใช้คู่กับ `SpeciesLoader.is_complete` ในการรีเฟรชหน้าแรก)"""
        return self.status not in (None, CHECKING)

    @property
    def update_available(self):
        return self.status == AVAILABLE

    def check(self):
        """ถาม GitHub หนึ่งครั้ง คืนสถานะ ไม่โยน exception ไม่ว่ากรณีใด"""
        try:
            response = self.http.get(
                LATEST_RELEASE_API,
                headers={"Accept": "application/vnd.github+json"},
                timeout=TIMEOUT,
            )
        except requests.RequestException as error:
            return self._unknown(f"เชื่อมต่อ GitHub ไม่ได้: {type(error).__name__}")

        if response.status_code == 404:
            return self._unknown("ยังไม่มี release บน GitHub")
        if response.status_code != 200:
            return self._unknown(f"GitHub ตอบกลับ HTTP {response.status_code}")

        try:
            data = response.json()
            tag = data["tag_name"]
        except (ValueError, KeyError, TypeError):
            return self._unknown("ข้อมูล release อ่านไม่ได้")

        latest = parse_version(tag)
        current = parse_version(self.current)
        if latest is None or current is None:
            return self._unknown(f"รูปแบบเวอร์ชันไม่ถูกต้อง ({tag})")

        self.latest = ".".join(str(part) for part in latest)
        if isinstance(data.get("html_url"), str):
            self.url = data["html_url"]
        self.last_error = None
        self.status = AVAILABLE if latest > current else LATEST
        return self.status

    def _unknown(self, reason):
        self.last_error = reason
        self.status = UNKNOWN
        return self.status

    def status_text(self):
        """ข้อความสำหรับหน้าแรก"""
        if self.status == AVAILABLE:
            return (f"มีเวอร์ชันใหม่ v{self.latest} (คุณเล่นอยู่ v{self.current}) "
                    "— กดปุ่มด้านล่างเพื่อไปหน้าดาวน์โหลด")
        if self.status == LATEST:
            return f"v{self.current} · เป็นเวอร์ชันล่าสุดแล้ว"
        if self.status == CHECKING:
            return f"v{self.current} · กำลังตรวจหาเวอร์ชันใหม่..."
        if self.status == UNKNOWN:
            return f"v{self.current} · ตรวจหาเวอร์ชันใหม่ไม่ได้ ({self.last_error})"
        return f"v{self.current}"
