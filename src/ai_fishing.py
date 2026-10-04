"""ตัวช่วยตกปลาแบบเอเจนต์: สร้างเควสต์และเลือกปลาตามประวัติผู้เล่น

เอเจนต์ทำงานในเครื่อง ไม่ต้องใช้ API key หรืออินเทอร์เน็ตเพิ่ม
การสุ่มเลือกปลาจะเพิ่มน้ำหนักให้ชนิดที่ผู้เล่นยังจับได้น้อย
"""

import random
from datetime import date

from src.fish import BRACKISH, FRESHWATER, MARINE

QUEST_LABELS = {
    FRESHWATER: "ทะเลสาบน้ำจืด",
    MARINE: "ทะเลลึก",
    BRACKISH: "ปากแม่น้ำน้ำกร่อย",
}
QUEST_TEMPLATES = (
    {"id": "freshwater", "kind": "location", "location": FRESHWATER,
     "title": "นักสำรวจน้ำจืด"},
    {"id": "marine", "kind": "location", "location": MARINE,
     "title": "นักล่าปลาทะเล"},
    {"id": "brackish", "kind": "location", "location": BRACKISH,
     "title": "ผู้พิชิตปากแม่น้ำ"},
    {"id": "any_fish", "kind": "any", "title": "ออกเรือหาปลา"},
    {"id": "heavy_fish", "kind": "heavy", "title": "นักตกปลาร่างยักษ์"},
)


class AIFishingAgent:
    """สร้างเป้าหมายรายวันและปรับโอกาสสุ่มปลาตามกระเป๋าของผู้เล่น"""

    def __init__(self, state, rng=None):
        self.state = state
        self.rng = rng or random
        saved_quests = state.quest_data
        self.quests = saved_quests.get("quests")
        self.quest_date = saved_quests.get("date")

    def daily_quests(self, today=None):
        """คืนเควสต์ 1–5 รายการของวันนี้ โดยไม่สุ่มประเภทซ้ำกัน"""
        today = today or date.today()
        today_key = today.isoformat()
        if self.quests is None or self.quest_date != today_key:
            level_score = max(
                0, self.state.bait_level + self.state.rod_level - 2
            )
            count = self.rng.randint(1, len(QUEST_TEMPLATES))
            selected = self.rng.sample(QUEST_TEMPLATES, count)
            quests = []
            for template in selected:
                target = 2 + level_score
                min_weight = (
                    4.0 + (self.state.bait_level - 1) * 0.5
                    + (self.state.rod_level - 1) * 1.5
                )
                if template["kind"] == "heavy":
                    target = 1 + level_score // 3
                reward_base = 60 if template["kind"] == "any" else 90
                if template["kind"] == "heavy":
                    reward_base = 140
                quests.append({
                    **template,
                    "date": today_key,
                    "target": target,
                    "min_weight": min_weight,
                    "progress": 0,
                    "reward": reward_base + target * 25 + level_score * 20,
                    "claimed": False,
                })
            self.quests = quests
            self.quest_date = today_key
            self._save_quest_data()
        return [dict(quest) for quest in self.quests]

    def _save_quest_data(self):
        self.state.quest_data = {
            "date": self.quest_date,
            "quests": [dict(quest) for quest in self.quests],
        }

    def daily_quest(self, today=None):
        """รองรับผู้เรียกเดิม โดยคืนเควสต์แรกของชุดประจำวัน"""
        return self.daily_quests(today)[0]

    def record_catch(self, fish, today=None):
        """เพิ่มความคืบหน้าทุกเควสต์ที่ปลาที่จับได้ตรงตามเงื่อนไข"""
        self.daily_quests(today)
        for quest in self.quests:
            if quest["claimed"] or quest["progress"] >= quest["target"]:
                continue
            matches = (
                quest["kind"] == "any"
                or (quest["kind"] == "location"
                    and fish.location == quest["location"])
                or (quest["kind"] == "heavy"
                    and fish.weight_kg >= quest["min_weight"])
            )
            if matches:
                quest["progress"] += 1
        self._save_quest_data()
        return self.daily_quests(today)

    def claim_reward(self, quest_id, today=None):
        """รับรางวัลของเควสต์ที่สำเร็จ โดยรับได้เควสต์ละครั้งเดียว"""
        quest = next((item for item in self.daily_quests(today)
                      if item["id"] == quest_id), None)
        if (quest is None or quest["progress"] < quest["target"]
                or quest["claimed"]):
            return 0
        self.state.money += quest["reward"]
        claimed_quest = next(
            item for item in self.quests if item["id"] == quest_id
        )
        claimed_quest["claimed"] = True
        self._save_quest_data()
        return quest["reward"]

    def choose_species(self, api, location, rng=None):
        """สุ่มชนิดปลาโดยให้น้ำหนักมากขึ้นกับชนิดที่จับได้น้อย"""
        generator = rng or self.rng
        counts = {}
        for fish in self.state.inventory:
            if fish.location == location:
                counts[fish.name.casefold()] = (
                    counts.get(fish.name.casefold(), 0) + 1
                )

        # ใช้ random_species() เพื่อให้ทำงานได้ทั้งกับ FishAPI และ SpeciesLoader
        # ซึ่งจะคืนปลาสำรองทันทีระหว่างที่ข้อมูลออนไลน์กำลังโหลด
        candidates = [api.random_species(location, rng=generator)
                      for _ in range(3)]
        least_caught = min(
            counts.get(item.get("name", "").casefold(), 0)
            for item in candidates
        )
        preferred = [
            item for item in candidates
            if counts.get(item.get("name", "").casefold(), 0) == least_caught
        ]
        return generator.choice(preferred)

    @staticmethod
    def quest_description(quest):
        """แปลงข้อมูลเควสต์เป็นข้อความภาษาไทยสำหรับหน้าจอ"""
        if quest["kind"] == "any":
            return f"จับปลาให้ได้ {quest['target']} ตัว"
        if quest["kind"] == "heavy":
            return (f"จับปลาน้ำหนักอย่างน้อย {quest['min_weight']:.1f} กก. "
                    f"ให้ได้ {quest['target']} ตัว")
        place = QUEST_LABELS.get(quest["location"], quest["location"])
        return f"จับปลาใน{place}ให้ได้ {quest['target']} ตัว"
