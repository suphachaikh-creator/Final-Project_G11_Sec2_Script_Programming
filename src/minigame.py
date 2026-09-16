"""มินิเกม QTE สู้แรงปลา (Sprint 2 — Back-End)

ตรรกะล้วนๆ ไม่มี input() และไม่มี print() ที่สำคัญคือ **ตัวจับเวลาถูกฉีดเข้ามาได้**
ตอนเล่นจริงใช้ time.monotonic ส่วนตอนทดสอบใส่นาฬิกาจำลอง จึงทดสอบได้โดยไม่ต้องรอเวลาจริง
"""

import random
import string
import time

MIN_TARGET_LENGTH = 6
MAX_TARGET_LENGTH = 12
BASE_TIME_LIMIT = 6.0
TIME_PER_ROD_LEVEL = 0.5
MIN_TIME_LIMIT = 4.0
TIME_BONUS_PER_HIT = 1.0


class QTEMinigame:
    """โจทย์ตัวอักษรที่ผู้เล่นต้องพิมพ์ให้ทันก่อนเวลาหมด"""

    def __init__(self, rod_level=1, rng=None, clock=None):
        self.rng = rng or random
        self.clock = clock or time.monotonic
        self.targets = self._make_targets()
        self.time_limit = self.time_limit_for(rod_level)
        self.hit_count = 0
        self.miss_count = 0
        self._started_at = None

    def _make_targets(self):
        """สุ่มลำดับตัวอักษรที่ผู้เล่นต้องพิมพ์"""
        length = self.rng.randint(MIN_TARGET_LENGTH, MAX_TARGET_LENGTH)
        return [self.rng.choice(string.ascii_lowercase) for _ in range(length)]

    @staticmethod
    def time_limit_for(rod_level):
        """คันเบ็ดเลเวลสูงขึ้นได้เวลาสู้ปลามากขึ้น"""
        return max(MIN_TIME_LIMIT, BASE_TIME_LIMIT + rod_level * TIME_PER_ROD_LEVEL)

    @property
    def total_targets(self):
        """จำนวนตัวอักษรทั้งหมดของโจทย์"""
        return len(self.targets)

    @property
    def current_target(self):
        """ตัวอักษรที่ต้องพิมพ์ในขณะนี้ คืนค่า None เมื่อครบแล้ว"""
        if self.hit_count >= self.total_targets:
            return None
        return self.targets[self.hit_count]

    @property
    def is_complete(self):
        """พิมพ์ครบทุกตัวแล้วหรือยัง"""
        return self.hit_count >= self.total_targets

    def start(self):
        """เริ่มจับเวลา"""
        self._started_at = self.clock()
        return self.time_limit

    def time_left(self):
        """เวลาที่เหลือ ติดลบไม่ได้ ถ้ายังไม่เริ่มจะคืนเวลาเต็ม"""
        if self._started_at is None:
            return self.time_limit
        remaining = self.time_limit - (self.clock() - self._started_at)
        return max(0.0, round(remaining, 1))

    def is_timed_out(self):
        """หมดเวลาแล้วหรือยัง"""
        return self.time_left() <= 0

    def submit(self, key):
        """ส่งตัวอักษรที่ผู้เล่นพิมพ์ คืนค่า True เมื่อถูกต้อง

        พิมพ์ถูกจะได้เวลาเพิ่ม เพื่อให้โจทย์ยาวยังเล่นจบได้
        """
        if self.is_complete or self.is_timed_out():
            return False

        if str(key).strip().lower() == self.current_target:
            self.hit_count += 1
            self._started_at += TIME_BONUS_PER_HIT
            return True

        self.miss_count += 1
        return False

    def result(self):
        """สรุปผลของรอบนี้"""
        return {
            "success": self.is_complete,
            "hits": self.hit_count,
            "misses": self.miss_count,
            "total": self.total_targets,
        }
