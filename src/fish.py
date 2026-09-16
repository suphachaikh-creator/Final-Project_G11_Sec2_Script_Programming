"""โดเมนของปลาหนึ่งตัว (Sprint 2 — Back-End)

คลาสนี้เก็บทั้งข้อมูลและกฎการคำนวณน้ำหนักกับราคา โดยไม่รู้จักหน้าจอ ไฟล์ หรือ API
"""

import random

MIN_BASE_WEIGHT = 0.5
MAX_BASE_WEIGHT = 5.0
PRICE_PER_KG = 15

FRESHWATER = "freshwater"
MARINE = "marine"
BRACKISH = "brackish"

LOCATIONS = (FRESHWATER, MARINE, BRACKISH)


class Fish:
    """ปลาที่ผู้เล่นจับได้หนึ่งตัว"""

    def __init__(self, name, location, weight_kg, price):
        self.name = name
        self.location = location
        self.weight_kg = weight_kg
        self.price = price

    @staticmethod
    def roll_weight(bait_level, rng=None):
        """สุ่มน้ำหนักปลา โดยเหยื่อเลเวลสูงขึ้นจะได้ปลาตัวใหญ่ขึ้น

        รับ rng เข้ามาได้เพื่อให้ทดสอบผลลัพธ์แบบกำหนดค่าตายตัวได้
        """
        generator = rng or random
        base = generator.uniform(MIN_BASE_WEIGHT, MAX_BASE_WEIGHT)
        multiplier = 1 + (bait_level * 0.5)
        return round(base * multiplier, 2)

    @staticmethod
    def price_for(weight_kg, bait_level):
        """คำนวณราคาจากน้ำหนักคูณกับเรทราคาและเลเวลเหยื่อ"""
        return int(weight_kg * PRICE_PER_KG * bait_level)

    @classmethod
    def catch(cls, name, location, bait_level, rng=None):
        """สร้างปลาที่จับได้หนึ่งตัวพร้อมคำนวณน้ำหนักและราคาให้เสร็จ"""
        weight = cls.roll_weight(bait_level, rng=rng)
        return cls(name, location, weight, cls.price_for(weight, bait_level))

    def to_dict(self):
        """แปลงเป็น dict เพื่อบันทึกลงไฟล์ JSON"""
        return {
            "name": self.name,
            "location": self.location,
            "weight_kg": self.weight_kg,
            "price": self.price,
        }

    @classmethod
    def from_dict(cls, data):
        """สร้างอ็อบเจกต์จากข้อมูลในไฟล์เซฟ ใช้ค่า default เมื่อฟิลด์ขาด"""
        return cls(
            name=data.get("name", "ปลาปริศนา"),
            location=data.get("location", FRESHWATER),
            weight_kg=data.get("weight_kg", 0.0),
            price=data.get("price", 0),
        )

    def __repr__(self):
        return f"Fish({self.name!r}, {self.weight_kg} kg, ${self.price})"
