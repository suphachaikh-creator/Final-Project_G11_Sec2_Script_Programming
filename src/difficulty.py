"""ปรับความยากของมินิเกมอัตโนมัติ (Final Sprint)

ดูสถิติการเล่นย้อนหลังแล้วปรับเวลาและความยาวโจทย์ให้เหมาะกับฝีมือผู้เล่น
ตรรกะล้วนๆ ไม่แตะหน้าจอ ไฟล์ และเครือข่าย จึงทดสอบได้ครบทุกเส้นทาง
ประวัติการเล่นถูกเก็บในไฟล์เซฟผ่าน `GameState.difficulty_data` (`to_dict()` / `from_dict()`)

หลักสำคัญคือ **ต้องมีทั้งพื้นและเพดาน** ไม่ว่าผู้เล่นจะเก่งหรือแย่แค่ไหน
เวลาต้องไม่ต่ำกว่าขั้นต่ำจนเล่นไม่ได้ และไม่สูงจนเกมไม่ท้าทาย
"""

import string

from src.minigame import (MAX_TARGET_LENGTH, MIN_TARGET_LENGTH, MIN_TIME_LIMIT,
                          QTEMinigame)

MAX_TIME_LIMIT = 12.0
EASY_THRESHOLD = 0.4
HARD_THRESHOLD = 0.8
TIME_STEP = 1.0
LENGTH_STEP = 1
MIN_ROUNDS = 3
# ประวัติถูกเก็บในไฟล์เซฟ จึงเก็บแค่รอบล่าสุด ไม่ให้ไฟล์โตขึ้นทุกครั้งที่เล่น
MAX_HISTORY = 20

EASY = "easy"
NORMAL = "normal"
HARD = "hard"


def hit_rate(rounds):
    """อัตราการกดทันจากผลเล่นย้อนหลัง คืน 0.0 เมื่อยังไม่มีข้อมูล

    `rounds` คือลิสต์ของ dict ที่ `QTEMinigame.result()` คืนมา
    """
    hits = sum(item.get("hits", 0) for item in rounds)
    total = sum(item.get("total", 0) for item in rounds)
    if not total:
        return 0.0
    return round(hits / total, 2)


def clamp(value, low, high):
    """บีบค่าให้อยู่ในช่วงที่กำหนด"""
    return max(low, min(high, value))


class DifficultyTuner:
    """ตัดสินว่าโจทย์รอบถัดไปควรยากขึ้นหรือง่ายลง"""

    def __init__(self, rounds=None, min_rounds=MIN_ROUNDS):
        self.rounds = list(rounds or [])[-MAX_HISTORY:]
        self.min_rounds = min_rounds

    def record(self, result):
        """เก็บผลการเล่นหนึ่งรอบ ทิ้งรอบเก่าที่เกิน `MAX_HISTORY`"""
        self.rounds.append(dict(result))
        del self.rounds[:-MAX_HISTORY]
        return len(self.rounds)

    def recent(self, count=5):
        """ผลเล่นล่าสุดไม่เกินจำนวนที่ระบุ"""
        return self.rounds[-count:]

    def hit_rate(self):
        """อัตราการกดทันของรอบล่าสุด"""
        return hit_rate(self.recent())

    def level(self):
        """ระดับความยากที่เหมาะกับผู้เล่นตอนนี้

        ถ้ายังเล่นไม่ครบขั้นต่ำจะคืน `normal` ไว้ก่อน เพราะข้อมูลน้อยเกินกว่าจะตัดสิน
        """
        if len(self.rounds) < self.min_rounds:
            return NORMAL

        rate = self.hit_rate()
        if rate >= HARD_THRESHOLD:
            return HARD
        if rate <= EASY_THRESHOLD:
            return EASY
        return NORMAL

    def time_limit_for(self, rod_level):
        """เวลาของรอบถัดไป ไม่ต่ำกว่าขั้นต่ำและไม่เกินเพดาน"""
        base = QTEMinigame.time_limit_for(rod_level)
        shift = {HARD: -TIME_STEP, EASY: TIME_STEP}.get(self.level(), 0.0)
        return clamp(round(base + shift, 1), MIN_TIME_LIMIT, MAX_TIME_LIMIT)

    def target_length_for(self, rod_level):
        """ความยาวโจทย์ของรอบถัดไป อยู่ในช่วงที่มินิเกมรองรับเสมอ"""
        base = MIN_TARGET_LENGTH + rod_level
        shift = {HARD: LENGTH_STEP, EASY: -LENGTH_STEP}.get(self.level(), 0)
        return clamp(base + shift, MIN_TARGET_LENGTH, MAX_TARGET_LENGTH)

    def settings_for(self, rod_level):
        """สรุปค่าที่จะใช้ตั้งรอบถัดไป"""
        return {
            "level": self.level(),
            "hit_rate": self.hit_rate(),
            "time_limit": self.time_limit_for(rod_level),
            "target_length": self.target_length_for(rod_level),
        }

    def apply_to(self, minigame, rod_level, rng=None):
        """ปรับมินิเกมที่สร้างมาแล้วให้เข้ากับฝีมือผู้เล่น

        ทำแบบนี้แทนการแก้ `minigame.py` เพราะ `QTEMinigame` เป็นของ Sprint 2
        สปรินต์นี้จึงปรับจากภายนอกโดยไม่ไปแตะชั้นเดิม
        """
        settings = self.settings_for(rod_level)
        minigame.time_limit = settings["time_limit"]

        generator = rng or minigame.rng
        length = settings["target_length"]
        minigame.targets = [generator.choice(string.ascii_lowercase)
                            for _ in range(length)]
        return settings

    def to_dict(self):
        """เก็บลงไฟล์เซฟได้"""
        return {"rounds": self.rounds}

    @classmethod
    def from_dict(cls, data):
        """อ่านกลับจากไฟล์เซฟ ใช้ค่าว่างเมื่อฟิลด์ขาด"""
        rounds = (data or {}).get("rounds")
        return cls(rounds if isinstance(rounds, list) else [])
