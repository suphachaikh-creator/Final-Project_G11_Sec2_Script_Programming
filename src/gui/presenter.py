"""ตรรกะของหน้าจอ GUI (Sprint 3 — Full-Stack)

ไฟล์นี้ตั้งใจ **ไม่ import tkinter** เลยแม้แต่บรรทัดเดียว หน้าที่ของมันคือ
"ตัดสินใจ" ว่าหน้าจอควรแสดงอะไรและปุ่มไหนควรกดได้ ส่วนการวาดจริงอยู่ใน
`app.py` กับไฟล์ใน `pages/`

แยกแบบนี้เพราะเครื่องที่รัน CI ไม่มีจอ ถ้าเทสต์ต้องสร้าง `tk.Tk()` จะพังทันที
เมื่อตรรกะอยู่ในไฟล์นี้ เทสต์จึงยิงตรงมาได้โดยไม่ต้องเปิดหน้าต่าง
"""

from src.fish import BRACKISH, FRESHWATER, MARINE
from src.game_state import (FishNotFoundError, FishProtectedError,
                            NotEnoughMoneyError)
from src.minigame import QTEMinigame
from src.validators import validate_fish_name

LOCATION_LABELS = {
    FRESHWATER: "ทะเลสาบน้ำจืด",
    MARINE: "ทะเลลึก",
    BRACKISH: "ปากแม่น้ำน้ำกร่อย",
}

COLUMNS = ("name", "location", "weight", "price")
COLUMN_LABELS = {
    "name": "ชื่อปลา",
    "location": "แหล่งน้ำ",
    "weight": "น้ำหนัก (กก.)",
    "price": "ราคา ($)",
}
SORTABLE = ("name", "weight", "price")

ALL_LOCATIONS = "all"


def location_label(location):
    """แปลงรหัสแหล่งน้ำเป็นชื่อภาษาไทย ถ้าไม่รู้จักให้คืนค่าเดิม"""
    return LOCATION_LABELS.get(location, location)


class TkClock:
    """นาฬิกาที่เดินตามจังหวะของ `root.after()` แทนเวลาจริงของระบบ

    `QTEMinigame` รับนาฬิกาเข้ามาทาง constructor อยู่แล้วตั้งแต่ Sprint 2
    การเปลี่ยนมาใช้ตัวจับเวลาของ tkinter จึงทำได้โดยไม่ต้องแก้ `minigame.py` เลย
    """

    def __init__(self, interval_ms=100):
        self.interval = interval_ms / 1000.0
        self.now = 0.0

    def __call__(self):
        """ให้ใช้แทนฟังก์ชันนาฬิกาได้โดยตรง"""
        return self.now

    def tick(self):
        """เดินหน้าหนึ่งจังหวะ เรียกจากคอลแบ็กของ `root.after()`"""
        self.now += self.interval
        return self.now


class InventoryPresenter:
    """ตัดสินใจว่าตารางคลังสินค้าจะแสดงแถวไหนบ้าง และเรียงอย่างไร

    สถานะการค้นหา กรอง และเรียงลำดับเก็บไว้ที่นี่ ไม่ได้เก็บไว้ในวิดเจ็ต
    """

    def __init__(self, state):
        self.state = state
        self.keyword = ""
        self.location_filter = ALL_LOCATIONS
        self.sort_key = "price"
        self.descending = True

    def toggle_sort(self, key):
        """คลิกหัวคอลัมน์ คอลัมน์เดิมคือสลับทิศ คอลัมน์ใหม่คือเริ่มจากมากไปน้อย"""
        if key not in SORTABLE:
            raise ValueError(f"คอลัมน์ '{key}' เรียงลำดับไม่ได้")
        if key == self.sort_key:
            self.descending = not self.descending
        else:
            self.sort_key = key
            self.descending = True
        return self.sort_key, self.descending

    def heading_text(self, key):
        """ข้อความบนหัวคอลัมน์ พร้อมลูกศรบอกทิศทางการเรียง"""
        label = COLUMN_LABELS[key]
        if key != self.sort_key or key not in SORTABLE:
            return label
        return f"{label} {'▼' if self.descending else '▲'}"

    def visible_fish(self):
        """ปลาที่ควรแสดงในตาราง หลังผ่านการค้นหา กรอง และเรียงลำดับ

        เรียกใช้เมธอดเดิมของ `GameState` ทั้งหมด ไม่เขียนตรรกะซ้ำ
        """
        fish_list = self.state.sort_inventory(self.sort_key, self.descending)

        if self.keyword.strip():
            matched = self.state.search_inventory(self.keyword)
            fish_list = [fish for fish in fish_list if fish in matched]

        if self.location_filter != ALL_LOCATIONS:
            fish_list = [fish for fish in fish_list
                         if fish.location == self.location_filter]

        return fish_list

    def visible_rows(self):
        """แปลงปลาที่ต้องแสดงเป็นทูเพิลของข้อความ พร้อมใส่ลงตารางได้ทันที"""
        rows = []
        for fish in self.visible_fish():
            # ปลาที่เก็บไว้ติดดาวหน้าชื่อ ผู้เล่นจึงเห็นได้ทันทีว่าตัวไหนขายไม่ได้
            label = f"★ {fish.name}" if fish.keep else fish.name
            rows.append((label, location_label(fish.location),
                         f"{fish.weight_kg:.2f}", str(fish.price)))
        return rows

    def summary_lines(self):
        """ข้อความสรุปสถิติ คำนวณจาก GameState.summary() ไม่ได้ดึงจาก API"""
        stats = self.state.summary()
        if not stats["count"]:
            return ["ยังไม่มีปลาในกระเป๋า"]

        heaviest = stats["heaviest"]
        return [
            f"จำนวนปลา {stats['count']} ตัว",
            f"มูลค่ารวม ${stats['total_price']}",
            f"น้ำหนักเฉลี่ย {stats['average_weight']} กก.",
            f"ตัวที่หนักที่สุด {heaviest.name} ({heaviest.weight_kg} กก.)",
        ]

    def sell_all(self):
        """ขายปลาทั้งกระเป๋า ยกเว้นตัวที่เก็บไว้ คืนข้อความสำหรับแสดงบนหน้าจอ"""
        if not self.state.inventory:
            return "ยังไม่มีปลาให้ขาย"
        kept = len(self.state.kept_fish())
        earned = self.state.sell_all()
        if not earned:
            return "ไม่มีปลาที่ขายได้ ทุกตัวถูกเก็บไว้"
        if kept:
            return f"ขายปลาได้ ${earned} · เก็บไว้ {kept} ตัว"
        return f"ขายปลาได้ ${earned}"

    # ------------------------------------------------- ขายทีละตัวและยกชนิด
    def fish_at(self, index):
        """ปลาที่อยู่แถวที่ระบุของตาราง คืน None เมื่อแถวไม่มีอยู่จริง

        ลำดับตรงกับ `visible_rows()` เสมอ เพราะทั้งคู่อ่านจาก `visible_fish()`
        """
        if index is None:
            return None
        fish_list = self.visible_fish()
        if 0 <= index < len(fish_list):
            return fish_list[index]
        return None

    def species_count_at(self, index):
        """จำนวนปลาชนิดเดียวกับแถวที่เลือก ใช้ตั้งข้อความบนปุ่ม"""
        fish = self.fish_at(index)
        if fish is None:
            return 0
        return self.state.count_species(fish.name)

    # ------------------------------------------------- แก้ไขข้อมูล (Update)
    def rename_at(self, index, new_name):
        """ตั้งชื่อเล่นให้ปลาแถวที่เลือก คืนข้อความสำหรับแสดงบนหน้าจอ"""
        fish = self.fish_at(index)
        if fish is None:
            return "ยังไม่ได้เลือกปลา"
        old = fish.name
        try:
            cleaned = validate_fish_name(new_name)
            self.state.rename_fish(fish, cleaned)
        except ValueError as error:
            return str(error)
        return f"เปลี่ยนชื่อ {old} เป็น {fish.name}"

    def toggle_keep_at(self, index):
        """สลับสถานะเก็บไว้ของปลาแถวที่เลือก"""
        fish = self.fish_at(index)
        if fish is None:
            return "ยังไม่ได้เลือกปลา"
        kept = self.state.toggle_keep(fish)
        return (f"เก็บ {fish.name} ไว้แล้ว ขายไม่ได้จนกว่าจะยกเลิก" if kept
                else f"ยกเลิกการเก็บ {fish.name} แล้ว ขายได้ตามปกติ")

    def keep_label_at(self, index):
        """ข้อความบนปุ่มเก็บไว้ เปลี่ยนตามสถานะของปลาที่เลือก"""
        fish = self.fish_at(index)
        if fish is None:
            return "เก็บไว้ไม่ขาย"
        return "ยกเลิกการเก็บ" if fish.keep else "เก็บไว้ไม่ขาย"

    # ------------------------------------------------------ ขายปลา (Delete)
    def sell_one(self, index):
        """ขายปลาตัวเดียวตามแถวที่เลือก"""
        fish = self.fish_at(index)
        if fish is None:
            return "ยังไม่ได้เลือกปลา"
        try:
            price = self.state.sell_fish(fish)
        except (FishProtectedError, FishNotFoundError) as error:
            return str(error)
        return f"ขาย {fish.name} ได้ ${price}"

    def sell_species_at(self, index):
        """ขายปลาทุกตัวที่เป็นชนิดเดียวกับแถวที่เลือก"""
        fish = self.fish_at(index)
        if fish is None:
            return "ยังไม่ได้เลือกปลา"
        count, total = self.state.sell_species(fish.name)
        return f"ขาย {fish.name} {count} ตัว ได้ ${total}"


class ShopPresenter:
    """ตัดสินใจว่าปุ่มซื้อในร้านค้าควรกดได้หรือไม่"""

    def __init__(self, state):
        self.state = state

    def items(self):
        """รายการสินค้าพร้อมสถานะว่ากดได้หรือไม่ ใช้ตั้งค่า state ของปุ่ม"""
        return [
            {
                "key": "bait",
                "label": f"อัปเกรดเหยื่อ → เลเวล {self.state.bait_level + 1}",
                "cost": self.state.bait_cost,
                "enabled": self.state.can_afford(self.state.bait_cost),
            },
            {
                "key": "rod",
                "label": f"อัปเกรดคันเบ็ด → เลเวล {self.state.rod_level + 1}",
                "cost": self.state.rod_cost,
                "enabled": self.state.can_afford(self.state.rod_cost),
            },
        ]

    def buy(self, key):
        """ซื้อสินค้าหนึ่งรายการ คืน (สำเร็จหรือไม่, ข้อความ)"""
        actions = {"bait": self.state.upgrade_bait, "rod": self.state.upgrade_rod}
        if key not in actions:
            return False, f"ไม่มีสินค้าชื่อ '{key}'"

        try:
            level = actions[key]()
        except NotEnoughMoneyError as error:
            return False, str(error)

        name = "เหยื่อ" if key == "bait" else "คันเบ็ด"
        return True, f"อัปเกรด{name}เป็นเลเวล {level} แล้ว"


class FishingPresenter:
    """คุมรอบการตกปลาหนึ่งรอบ ตั้งแต่เริ่มมินิเกมจนเก็บปลาลงกระเป๋า

    รับ `clock` เข้ามาได้เหมือนเดิม ตอนเล่นจริง `app.py` จะส่งนาฬิกาที่เดินคู่ไปกับ
    `root.after()` ส่วนตอนทดสอบใส่นาฬิกาจำลอง จึงไม่ต้องรอเวลาจริง
    """

    def __init__(self, state, api, rng=None, clock=None, ai_agent=None):
        self.state = state
        self.api = api
        self.rng = rng
        self.clock = clock
        self.ai_agent = ai_agent
        self.location = FRESHWATER
        self.minigame = None
        self.last_result = None

    def start(self, location):
        """เริ่มรอบใหม่ที่แหล่งน้ำที่เลือก"""
        self.location = location
        self.last_result = None
        self.minigame = QTEMinigame(self.state.rod_level, rng=self.rng, clock=self.clock)
        self.minigame.start()
        return self.minigame

    @property
    def is_running(self):
        """ยังเล่นรอบนี้อยู่หรือไม่"""
        if self.minigame is None:
            return False
        return not (self.minigame.is_complete or self.minigame.is_timed_out())

    def target_text(self):
        """ตัวอักษรที่ต้องพิมพ์ทั้งหมด โดยตัวที่พิมพ์ไปแล้วจะกลายเป็นจุด"""
        if self.minigame is None:
            return ""
        done = self.minigame.hit_count
        return " ".join("·" * done + "".join(self.minigame.targets[done:]))

    def timer_text(self):
        """ข้อความเวลาที่เหลือ"""
        if self.minigame is None:
            return "0.0 วินาที"
        return f"{self.minigame.time_left():.1f} วินาที"

    def progress_ratio(self):
        """สัดส่วนเวลาที่เหลือ 0.0–1.0 ใช้ตั้งค่าแถบเวลา"""
        if self.minigame is None or not self.minigame.time_limit:
            return 0.0
        return max(0.0, min(1.0, self.minigame.time_left() / self.minigame.time_limit))

    def press(self, key):
        """ส่งปุ่มที่ผู้เล่นกด คืน True เมื่อกดถูก"""
        if not self.is_running:
            return False
        return self.minigame.submit(key)

    def finish(self):
        """ปิดรอบ ถ้าสำเร็จจะเก็บปลาลงกระเป๋าให้ด้วย"""
        if self.minigame is None:
            return None

        result = self.minigame.result()
        result["fish"] = None
        if result["success"]:
            if self.ai_agent is None:
                species = self.api.random_species(self.location, rng=self.rng)
            else:
                species = self.ai_agent.choose_species(
                    self.api, self.location, rng=self.rng
                )
            result["fish"] = self.state.add_fish(
                self._make_fish(species["name"]))
            if self.ai_agent is not None:
                result["quest"] = self.ai_agent.record_catch(result["fish"])

        self.last_result = result
        return result

    def _make_fish(self, name):
        """สร้างปลาที่จับได้ แยกออกมาเพื่อให้เทสต์แทนที่ได้ง่าย"""
        from src.fish import Fish
        return Fish.catch(name, self.location, self.state.bait_level, rng=self.rng)

    def result_text(self):
        """ข้อความสรุปผลรอบล่าสุด"""
        if not self.last_result:
            return ""
        if not self.last_result["success"]:
            return f"ปลาหลุด! พิมพ์ทัน {self.last_result['hits']} ตัว"
        fish = self.last_result["fish"]
        return f"ได้ {fish.name} หนัก {fish.weight_kg} กก. ขายได้ ${fish.price}"


class DashboardPresenter:
    """ข้อความบนหน้าแรก"""

    def __init__(self, state, api=None):
        self.state = state
        self.api = api

    def status_lines(self):
        """สถานะผู้เล่นแบบย่อ"""
        return [
            f"เงิน ${self.state.money}",
            f"เหยื่อเลเวล {self.state.bait_level}",
            f"คันเบ็ดเลเวล {self.state.rod_level}",
            f"ปลาในกระเป๋า {len(self.state.inventory)} ตัว",
        ]

    def api_status(self):
        """บอกผู้เล่นว่ากำลังใช้ข้อมูลออนไลน์ ข้อมูลสำรอง หรือกำลังโหลดอยู่

        ตัวโหลดเบื้องหลังมี `status_text()` ของตัวเองที่บอกได้ละเอียดกว่า
        ถ้ามีก็ใช้อันนั้น ถ้าไม่มีก็ถอยไปดูแค่ธง `using_fallback`
        """
        if self.api is None:
            return ""
        describe = getattr(self.api, "status_text", None)
        if callable(describe):
            return describe()
        if getattr(self.api, "using_fallback", False):
            return "ออฟไลน์ — ใช้ข้อมูลปลาสำรองในเครื่อง"
        return "ออนไลน์ — ข้อมูลปลาจาก WoRMS + Open Fisheries"
