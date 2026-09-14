"""File I/O และตัวเชื่อม API ของ Sprint 2 (Back-End)"""

import json
import os

from src.api_client import APIClient
from src.key import GEMINI_API_KEY
from src.pet import Pet

# บันทึกไฟล์เซฟไว้ที่โฟลเดอร์ data นอก src (ระดับ Root ของ Sprint2)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAVE_DIR = os.path.join(BASE_DIR, "data")
SAVE_FILE = os.path.join(SAVE_DIR, "pet_state.json")


def ensure_dir():
    """สร้างโฟลเดอร์ data ถ้ายังไม่มี"""
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)


def save_game(pet):
    """บันทึกสถานะน้องแมวลงไฟล์ JSON"""
    ensure_dir()
    with open(SAVE_FILE, "w", encoding="utf-8") as save_file:
        json.dump(pet.to_dict(), save_file, ensure_ascii=False, indent=4)


def load_game():
    """โหลดข้อมูลจาก data/pet_state.json คืนค่า None เมื่อไม่มีไฟล์หรือไฟล์เสีย"""
    if not os.path.exists(SAVE_FILE):
        return None

    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as save_file:
            return Pet.from_dict(json.load(save_file))
    except (json.JSONDecodeError, OSError, KeyError, TypeError):
        return None


def fetch_new_pets(limit=3):
    """ดึงข้อมูลสายพันธุ์แมวผ่าน api_client.py คืนค่า list ว่างเมื่อเรียกไม่สำเร็จ"""
    try:
        return APIClient.get_cats_from_gemini(api_key=GEMINI_API_KEY, limit=limit)
    except Exception as error:
        print(f"\n[เกิดข้อผิดพลาดในการดึง API]: {error}")
        return []
