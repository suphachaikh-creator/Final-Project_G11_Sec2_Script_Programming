"""ประวัติการจับปลาแบบ append-only และสถิติย้อนหลัง (Final Sprint)

กระเป๋าปลาใน `GameState` เก็บเฉพาะปลาที่ยังไม่ขาย พอขายแล้วข้อมูลก็หายไปด้วย
ไฟล์นี้จึงจดทุกครั้งที่จับปลาได้ลง `data/catch_log.jsonl` บรรทัดละหนึ่งตัว
**เขียนต่อท้ายอย่างเดียว ไม่เขียนทับของเดิม** ประวัติจึงไม่หายแม้ขายปลาไปแล้ว

แยกจาก `save_game.json` โดยตั้งใจ เพราะแต่ละบรรทัดเป็นเหตุการณ์ที่จบในตัวเอง
ไม่มีค่าใดในไฟล์เซฟคำนวณมาจากไฟล์นี้ บันทึกคนละจังหวะจึงไม่ทำให้ข้อมูลขัดกัน

เหมือน `SaveManager` ตรงที่ **ไฟล์หายหรือมีบรรทัดเสียต้องไม่ทำให้เกม crash**
"""

import json
import os
from collections import Counter
from datetime import datetime

from src.fish import LOCATIONS

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_LOG_FILE = os.path.join(BASE_DIR, "data", "catch_log.jsonl")


def _now():
    return datetime.now().isoformat(timespec="seconds")


class CatchLog:
    """จดปลาที่จับได้ทุกตัวลงไฟล์ JSON Lines แล้วอ่านกลับมาสรุปผล"""

    def __init__(self, log_file=DEFAULT_LOG_FILE, clock=None):
        self.log_file = log_file
        # ฉีดนาฬิกาเข้ามาได้ เทสต์จึงกำหนดเวลาที่บันทึกได้แน่นอน
        self.clock = clock or _now
        self.last_error = None
        self.skipped = 0

    def record(self, fish):
        """ต่อท้ายปลาหนึ่งตัวลงไฟล์ คืน True เมื่อสำเร็จ

        บันทึกไม่สำเร็จไม่โยน exception เพราะประวัติเป็นข้อมูลเสริม
        ไม่ควรทำให้การจับปลาครั้งนั้นล้มเหลวไปด้วย
        """
        entry = {
            "name": fish.name,
            "location": fish.location,
            "weight_kg": fish.weight_kg,
            "price": fish.price,
            "caught_at": self.clock(),
        }
        try:
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
            with open(self.log_file, "a", encoding="utf-8") as handle:
                handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
            self.last_error = None
            return True
        except OSError as error:
            self.last_error = f"บันทึกประวัติไม่สำเร็จ: {type(error).__name__}"
            return False

    def entries(self):
        """อ่านประวัติทั้งหมด ข้ามบรรทัดที่เสียแล้วนับไว้ใน `skipped`

        บรรทัดสุดท้ายอาจขาดครึ่งถ้าโปรแกรมถูกปิดระหว่างเขียน
        ข้ามแค่บรรทัดนั้น ประวัติที่เหลือยังใช้ได้ครบ
        """
        self.skipped = 0
        if not os.path.exists(self.log_file):
            return []

        result = []
        try:
            with open(self.log_file, encoding="utf-8") as handle:
                for line in handle:
                    if not line.strip():
                        continue
                    entry = _parse(line)
                    if entry is None:
                        self.skipped += 1
                    else:
                        result.append(entry)
        except (OSError, UnicodeDecodeError) as error:
            self.last_error = f"อ่านประวัติไม่สำเร็จ: {type(error).__name__}"
            return result
        self.last_error = None
        return result

    def summary(self):
        """สรุปสถิติจากประวัติทั้งหมดในไฟล์"""
        return summarize(self.entries())


def _parse(line):
    """แปลงหนึ่งบรรทัดเป็น dict คืน None ถ้าข้อมูลใช้ไม่ได้"""
    try:
        entry = json.loads(line)
    except ValueError:
        return None
    if not isinstance(entry, dict):
        return None
    name = entry.get("name")
    weight = entry.get("weight_kg")
    price = entry.get("price")
    if not isinstance(name, str) or not name.strip():
        return None
    if not isinstance(weight, (int, float)) or not isinstance(price, (int, float)):
        return None
    if entry.get("location") not in LOCATIONS:
        return None
    return entry


def summarize(entries):
    """สรุปสถิติจากรายการประวัติ — ตรรกะล้วน ไม่แตะไฟล์ จึงทดสอบได้ตรงๆ

    คืนค่า
        count            จำนวนปลาที่จับได้ทั้งหมด
        total_weight     น้ำหนักรวม (กก.)
        average_weight   น้ำหนักเฉลี่ย (กก.)
        total_value      มูลค่ารวมของปลาที่จับได้ ณ ตอนจับ
        most_common      (ชื่อ, จำนวนครั้ง) ของชนิดที่จับได้บ่อยที่สุด หรือ None
        heaviest         รายการของปลาที่หนักที่สุด หรือ None
        by_location      {แหล่งน้ำ: {"count", "value"}} ครบทั้งสามแหล่ง
    """
    by_location = {code: {"count": 0, "value": 0} for code in LOCATIONS}
    if not entries:
        return {"count": 0, "total_weight": 0.0, "average_weight": 0.0,
                "total_value": 0, "most_common": None, "heaviest": None,
                "by_location": by_location}

    for entry in entries:
        place = by_location[entry["location"]]
        place["count"] += 1
        place["value"] += entry["price"]

    total_weight = round(sum(entry["weight_kg"] for entry in entries), 2)
    # ชื่อที่จับได้เท่ากัน ให้ชนิดที่จับได้ก่อนชนะ ผลจึงแน่นอนทุกครั้ง
    most_common = Counter(entry["name"] for entry in entries).most_common(1)[0]
    return {
        "count": len(entries),
        "total_weight": total_weight,
        "average_weight": round(total_weight / len(entries), 2),
        "total_value": sum(entry["price"] for entry in entries),
        "most_common": most_common,
        "heaviest": max(entries, key=lambda entry: entry["weight_kg"]),
        "by_location": by_location,
    }
