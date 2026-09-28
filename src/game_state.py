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


class FishNotFoundError(ValueError):
    """อ้างถึงปลาที่ไม่มีอยู่ในกระเป๋า

    สืบทอดจาก `ValueError` เพื่อให้โค้ดเดิมที่ดัก `ValueError` ยังทำงานได้
    แต่ผู้เรียกที่ต้องการแยกกรณีนี้ออกมาก็ดักคลาสนี้ตรงๆ ได้
    """


class FishProtectedError(ValueError):
    """ปลาถูกทำเครื่องหมายเก็บไว้ ต้องยกเลิกเครื่องหมายก่อนจึงจะขายได้"""


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

    # -------------------------------------------- แก้ไขข้อมูล (Update)
    def require_fish(self, fish):
        """ตรวจว่าปลาตัวนี้อยู่ในกระเป๋าจริง ถ้าไม่ใช่ให้โยน FishNotFoundError

        เทียบด้วยตัวตนของอ็อบเจกต์ ไม่ใช่ชื่อ ปลาชื่อซ้ำกันจึงไม่สับสน
        """
        if fish not in self.inventory:
            raise FishNotFoundError(f"ไม่พบ {fish.name} ในกระเป๋า")
        return fish

    def rename_fish(self, fish, new_name):
        """ตั้งชื่อเล่นให้ปลาที่จับได้ คืนชื่อใหม่

        ชื่อถูกตรวจความถูกต้องมาแล้วจากชั้น Validation ชั้นนี้จึงตรวจแค่
        เรื่องที่เป็นกฎของเกม คือปลาต้องมีอยู่จริงและชื่อต้องไม่ว่าง
        """
        self.require_fish(fish)
        cleaned = str(new_name).strip()
        if not cleaned:
            raise ValueError("ชื่อปลาห้ามเว้นว่าง")
        fish.name = cleaned
        return fish.name

    def set_keep(self, fish, keep):
        """ทำเครื่องหมายเก็บปลาไว้ไม่ให้ขาย หรือยกเลิกเครื่องหมาย"""
        self.require_fish(fish)
        fish.keep = bool(keep)
        return fish.keep

    def toggle_keep(self, fish):
        """สลับสถานะเก็บไว้ของปลาหนึ่งตัว"""
        return self.set_keep(fish, not fish.keep)

    def kept_fish(self):
        """ปลาที่ถูกทำเครื่องหมายเก็บไว้ทั้งหมด"""
        return [fish for fish in self.inventory if fish.keep]

    # --------------------------------------------- ขายปลา (Delete)
    def sell_all(self):
        """ขายปลาทั้งกระเป๋า ยกเว้นตัวที่ทำเครื่องหมายเก็บไว้

        คืนค่าเงินที่ได้รับ ปลาที่เก็บไว้จะยังอยู่ในกระเป๋าเหมือนเดิม
        """
        sellable = [fish for fish in self.inventory if not fish.keep]
        total = sum(fish.price for fish in sellable)
        self.money += total
        self.inventory = [fish for fish in self.inventory if fish.keep]
        return total

    def sell_fish(self, fish):
        """ขายปลาตัวเดียว คืนค่าเงินที่ได้รับ

        เทียบด้วยตัวตนของอ็อบเจกต์ ไม่ใช่ชื่อ ปลาชื่อซ้ำกันจึงขายผิดตัวไม่ได้
        """
        self.require_fish(fish)
        if fish.keep:
            raise FishProtectedError(
                f"{fish.name} ถูกเก็บไว้ ยกเลิกเครื่องหมายก่อนจึงจะขายได้")
        self.inventory.remove(fish)
        self.money += fish.price
        return fish.price

    def count_species(self, name):
        """นับว่ามีปลาชื่อนี้ในกระเป๋ากี่ตัว"""
        return sum(1 for fish in self.inventory if fish.name == name)

    def sell_species(self, name):
        """ขายปลาทุกตัวที่ชื่อตรงกัน คืนค่า (จำนวนตัว, เงินที่ได้รับ)"""
        if not any(fish.name == name for fish in self.inventory):
            raise FishNotFoundError(f"ไม่พบ {name} ในกระเป๋า")

        # ปลาที่ทำเครื่องหมายเก็บไว้จะไม่ถูกขายไปกับยกชนิด
        matched = [fish for fish in self.inventory
                   if fish.name == name and not fish.keep]
        total = sum(fish.price for fish in matched)
        self.inventory = [fish for fish in self.inventory if fish not in matched]
        self.money += total
        return len(matched), total

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
