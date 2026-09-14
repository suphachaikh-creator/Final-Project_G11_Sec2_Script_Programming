import os
import json
from key import GEMINI_API_KEY
from api_client import APIClient
from pet import Pet

# บันทึกไฟล์เซฟไว้ที่โฟลเดอร์ data นอก src (ระดับ Root)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAVE_DIR = os.path.join(BASE_DIR, "data")
SAVE_FILE = os.path.join(SAVE_DIR, "pet_state.json")

def ensure_dir():
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

def save_game(pet):
    """บันทึกสถานะน้องแมวลงไฟล์ JSON"""
    ensure_dir()
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(pet.to_dict(), f, ensure_ascii=False, indent=4)

def load_game():
    """โหลดข้อมูลจาก data/pet_state.json"""
    if not os.path.exists(SAVE_FILE):
        return None
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return Pet.from_dict(data)
    except Exception:
        return None

def fetch_new_pets():
    """ดึงข้อมูลสายพันธุ์แมวผ่าน api_client.py"""
    try:
        cats = APIClient.get_cats_from_gemini(api_key=GEMINI_API_KEY, limit=3)
        return cats
    except Exception as e:
        print(f"\n[เกิดข้อผิดพลาดในการดึง API]: {e}")
        return []