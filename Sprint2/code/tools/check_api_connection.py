"""สคริปต์ตรวจสอบการเชื่อมต่อ Gemini API ด้วยมือ (ไม่ใช่ unit test)

รันจากโฟลเดอร์ Sprint2 ด้วยคำสั่ง: python tools/check_api_connection.py
สคริปต์นี้ตั้งใจไม่ตั้งชื่อขึ้นต้นด้วย test_ เพื่อไม่ให้ pytest/CI เรียกใช้งาน
เพราะต้องใช้ API Key จริงและต้องต่ออินเทอร์เน็ต
"""

import os
import sys
import threading
import time

os.environ["PYTHONIOENCODING"] = "utf-8"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api_client import APIClient  # noqa: E402
from src.key import GEMINI_API_KEY  # noqa: E402


class LoadingTimer:
    """แสดงเวลาที่ผ่านไประหว่างรอผลลัพธ์จาก API"""

    def __init__(self):
        self._running = False
        self._thread = None

    def _tick(self):
        start_time = time.time()
        while self._running:
            elapsed = int(time.time() - start_time)
            sys.stdout.write(f"\r[Loading] กำลังทำงาน... ผ่านไป {elapsed} วินาที")
            sys.stdout.flush()
            time.sleep(1)

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._tick)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread is not None:
            self._thread.join()
        print("\n")


def check_fetch_cats_from_gemini(limit=5):
    """เรียก API จริงแล้วแสดงผลลัพธ์ออกหน้าจอ"""
    print("กำลังเรียกใช้งาน Gemini API เพื่อดึงและวิเคราะห์ข้อมูลแมว...")
    timer = LoadingTimer()
    timer.start()

    try:
        cats_data = APIClient.get_cats_from_gemini(api_key=GEMINI_API_KEY, limit=limit)
    except Exception as error:
        timer.stop()
        print(f"[เกิดข้อผิดพลาด]: {error}")
        return False

    timer.stop()

    if not cats_data:
        print("[X] API ตอบกลับแต่ไม่มีข้อมูล")
        return False

    for index, item in enumerate(cats_data[:limit], start=1):
        print(f"[{index}] สายพันธุ์: {item.get('breed')}")
        print(f"    ประเทศถิ่นกำเนิด     : {item.get('country')}")
        print(f"    นิสัย/พฤติกรรม       : {item.get('temperament')}")
        print(f"    คะแนนความดื้อ        : {item.get('stubbornness_score')} / 100")
        print(f"    รายละเอียดเล็กน้อย   : {item.get('description')}")
        print("-" * 60)

    print("\nดึงและวิเคราะห์ข้อมูลจาก Gemini สำเร็จเรียบร้อย!")
    return True


if __name__ == "__main__":
    sys.exit(0 if check_fetch_cats_from_gemini() else 1)
