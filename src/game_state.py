"""สถานะการเล่นและกฎทางธุรกิจทั้งหมด (Sprint 2 — Back-End)

คลาสนี้เป็นตรรกะบริสุทธิ์ ไม่มี input() ไม่มี print() ไม่แตะไฟล์ และไม่รู้จัก API
จึงเขียน unit test ได้ครบทุกเมธอดโดยไม่ต้องเตรียมสภาพแวดล้อมอะไรเลย
"""

from src.fish import Fish

START_MONEY = 100
UPGRADE_BASE_COST = 50

SORT_KEYS = {
    "name": lambda fish: fish.name.lower(),
    "weight": lambda fish: fish.weight_kg,
    "price": lambda fish: fish.price,
}


class NotEnoughMoneyError(Exception):
    """เงินไม่พอสำหรับรายการที่เลือก"""


class GameState:
    """เงิน กระเป๋าปลา และเลเวลอุปกรณ์ของผู้เล่น"""

    def __init__(self, money=START_MONEY, inventory=None, bait_level=1, rod_level=1):
        self.money = money
        self.inventory = list(inventory or [])
        self.bait_level = bait_level
        self.rod_level = rod_level

    # ------------------------------------------------------------------ ราคา
    @property
    def bait_cost(self):
        """ราคาอัปเกรดเหยื่อครั้งถัดไป"""
        return self.bait_level * UPGRADE_BASE_COST

    @property
    def rod_cost(self):
        """ราคาอัปเกรดคันเบ็ดครั้งถัดไป"""
        return self.rod_level * UPGRADE_BASE_COST

    def can_afford(self, cost):
        """ตรวจว่าเงินพอสำหรับราคาที่ระบุหรือไม่"""
        return self.money >= cost

    # ------------------------------------------------------------- การกระทำ
    def add_fish(self, fish):
        """เก็บปลาที่จับได้ลงกระเป๋า"""
        self.inventory.append(fish)
        return fish

    def sell_all(self):
        """ขายปลาทั้งกระเป๋า คืนค่าเงินที่ได้รับ"""
        total = sum(fish.price for fish in self.inventory)
        self.money += total
        self.inventory.clear()
        return total

    def upgrade_bait(self):
        """อัปเกรดเหยื่อ ถ้าเงินไม่พอจะโยน NotEnoughMoneyError"""
        cost = self.bait_cost
        if not self.can_afford(cost):
            raise NotEnoughMoneyError(f"ต้องใช้เงิน ${cost} แต่มีอยู่ ${self.money}")
        self.money -= cost
        self.bait_level += 1
        return self.bait_level

    def upgrade_rod(self):
        """อัปเกรดคันเบ็ด ถ้าเงินไม่พอจะโยน NotEnoughMoneyError"""
        cost = self.rod_cost
        if not self.can_afford(cost):
            raise NotEnoughMoneyError(f"ต้องใช้เงิน ${cost} แต่มีอยู่ ${self.money}")
        self.money -= cost
        self.rod_level += 1
        return self.rod_level

    # ------------------------------------------- ค้นหา กรอง และเรียงลำดับ
    def search_inventory(self, keyword):
        """ค้นปลาในกระเป๋าด้วยชื่อ (ไม่สนตัวพิมพ์เล็ก/ใหญ่)"""
        needle = keyword.strip().lower()
        return [fish for fish in self.inventory if needle in fish.name.lower()]

    def filter_inventory(self, location):
        """กรองปลาในกระเป๋าตามแหล่งน้ำ"""
        return [fish for fish in self.inventory if fish.location == location]

    def sort_inventory(self, key="price", descending=True):
        """เรียงลำดับปลาในกระเป๋าตามชื่อ น้ำหนัก หรือราคา"""
        if key not in SORT_KEYS:
            raise ValueError(f"เรียงลำดับด้วย '{key}' ไม่ได้ ใช้ได้เฉพาะ {sorted(SORT_KEYS)}")
        return sorted(self.inventory, key=SORT_KEYS[key], reverse=descending)

    def summary(self):
        """สรุปสถิติการจับปลาสำหรับหน้าคลังสินค้า"""
        if not self.inventory:
            return {"count": 0, "total_price": 0, "average_weight": 0.0, "heaviest": None}

        weights = [fish.weight_kg for fish in self.inventory]
        return {
            "count": len(self.inventory),
            "total_price": sum(fish.price for fish in self.inventory),
            "average_weight": round(sum(weights) / len(weights), 2),
            "heaviest": max(self.inventory, key=lambda fish: fish.weight_kg),
        }

    # -------------------------------------------------------- serialization
    def to_dict(self):
        """แปลงสถานะทั้งหมดเป็น dict เพื่อบันทึกลงไฟล์ JSON"""
        return {
            "money": self.money,
            "bait_level": self.bait_level,
            "rod_level": self.rod_level,
            "inventory": [fish.to_dict() for fish in self.inventory],
        }

    @classmethod
    def from_dict(cls, data):
        """สร้างสถานะจากข้อมูลในไฟล์เซฟ ใช้ค่า default เมื่อฟิลด์ขาด"""
        return cls(
            money=data.get("money", START_MONEY),
            inventory=[Fish.from_dict(item) for item in data.get("inventory", [])],
            bait_level=data.get("bait_level", 1),
            rod_level=data.get("rod_level", 1),
        )
