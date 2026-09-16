"""ชั้นบันทึกและโหลดไฟล์เซฟ (Sprint 2 — Back-End)

รับผิดชอบเรื่องไฟล์อย่างเดียว ไม่รู้จักหน้าจอและไม่รู้จัก API
ไฟล์หายหรือไฟล์เสียหายต้องไม่ทำให้เกม crash แต่ให้เริ่มเกมใหม่ได้
"""

import json
import os

from src.game_state import GameState

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_SAVE_FILE = os.path.join(BASE_DIR, "data", "save_game.json")


class SaveManager:
    """อ่านและเขียนสถานะการเล่นเป็นไฟล์ JSON"""

    def __init__(self, save_file=DEFAULT_SAVE_FILE):
        self.save_file = save_file
        self.last_error = None

    def exists(self):
        """มีไฟล์เซฟอยู่หรือไม่"""
        return os.path.exists(self.save_file)

    def save(self, state):
        """บันทึกสถานะลงไฟล์ คืนค่า True เมื่อสำเร็จ"""
        try:
            os.makedirs(os.path.dirname(self.save_file), exist_ok=True)
            with open(self.save_file, "w", encoding="utf-8") as handle:
                json.dump(state.to_dict(), handle, ensure_ascii=False, indent=4)
            self.last_error = None
            return True
        except OSError as error:
            self.last_error = f"บันทึกไฟล์ไม่สำเร็จ: {type(error).__name__}"
            return False

    def load(self):
        """โหลดสถานะจากไฟล์ คืนค่า None เมื่อไม่มีไฟล์หรือไฟล์เสียหาย"""
        if not self.exists():
            self.last_error = "ยังไม่มีไฟล์เซฟ"
            return None

        try:
            with open(self.save_file, encoding="utf-8") as handle:
                data = json.load(handle)
            if not isinstance(data, dict):
                raise ValueError("โครงสร้างไฟล์เซฟไม่ถูกต้อง")
            self.last_error = None
            return GameState.from_dict(data)
        except (json.JSONDecodeError, ValueError, OSError, TypeError, AttributeError) as error:
            self.last_error = f"ไฟล์เซฟเสียหาย: {type(error).__name__}"
            return None

    def load_or_new(self):
        """โหลดเซฟเดิม ถ้าไม่ได้ก็เริ่มเกมใหม่"""
        return self.load() or GameState()
