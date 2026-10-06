"""ตัวช่วยตกปลา: เชื่อม Gemini แบบเลือกใช้ พร้อมเอเจนต์สำรองในเครื่อง

การสุ่มเลือกปลาจะเพิ่มโอกาสให้ชนิดที่ผู้เล่นยังจับได้น้อย
"""

import json
import os
import random
import time
from datetime import date

import requests

from src.fish import BRACKISH, FRESHWATER, MARINE


def _load_project_env():
    """อ่านค่าตั้งค่าจาก .env ในโฟลเดอร์โปรเจกต์โดยไม่ทับค่าระบบ"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_file = os.path.join(project_root, ".env")
    try:
        with open(env_file, encoding="utf-8") as handle:
            lines = handle.readlines()
    except OSError:
        return

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        key, separator, value = line.partition("=")
        key = key.strip()
        if not separator or key not in {"GEMINI_API_KEY", "GEMINI_MODEL"}:
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if value:
            os.environ.setdefault(key, value)


_load_project_env()

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models"
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash")
GEMINI_TIMEOUT = 15
GEMINI_MAX_ATTEMPTS = 3
GEMINI_RETRY_STATUSES = {408, 429, 500, 502, 503, 504}
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
        self.ai_checked = bool(saved_quests.get("ai_checked", False))
        self.ai_connected = saved_quests.get("ai_connected")

    def daily_quests(self, today=None):
        """คืนเควสต์ 1–5 รายการของวันนี้ โดยไม่สุ่มประเภทซ้ำกัน"""
        today = today or date.today()
        today_key = today.isoformat()
        if self.quests is None or self.quest_date != today_key:
            return self.generate_local_quests(today, mark_checked=False)
        return [dict(quest) for quest in self.quests]

    def generate_local_quests(self, today=None, mark_checked=True):
        """สุ่มชุดเควสต์ใหม่ในเครื่อง พร้อมใช้เมื่อ Gemini ใช้งานไม่ได้"""
        today = today or date.today()
        today_key = today.isoformat()
        count = self.rng.randint(1, len(QUEST_TEMPLATES))
        selected = self.rng.sample(QUEST_TEMPLATES, count)
        self.quests = self._build_quests(selected, today_key)
        self.quest_date = today_key
        self.ai_checked = bool(mark_checked)
        self.ai_connected = False if mark_checked else None
        self._save_quest_data()
        return [dict(quest) for quest in self.quests]

    @property
    def gemini_configured(self):
        """True เมื่อมี API key สำหรับเรียก Gemini"""
        return bool(os.environ.get("GEMINI_API_KEY", "").strip())

    def generate_gemini_quests(self, today=None, apply=True, force=False):
        """ขอ Gemini เลือกและตั้งชื่อเควสต์ แล้วตรวจข้อมูลก่อนนำมาใช้

        Raises:
            RuntimeError: ไม่มี API key หรือ Gemini ตอบกลับผิดรูปแบบ/เรียกไม่สำเร็จ
        """
        if not self.gemini_configured:
            raise RuntimeError("ยังไม่ได้ตั้งค่า GEMINI_API_KEY")

        today = today or date.today()
        today_key = today.isoformat()
        previous_quests = self.daily_quests(today)
        if not force and any(
                quest["progress"] or quest["claimed"]
                for quest in previous_quests):
            raise RuntimeError("เริ่มสร้างชุด Gemini ใหม่ไม่ได้หลังเริ่มทำเควสต์แล้ว")

        template_by_id = {item["id"]: item for item in QUEST_TEMPLATES}
        allowed_ids = list(template_by_id)
        schema = {
            "type": "OBJECT",
            "properties": {
                "quests": {
                    "type": "ARRAY",
                    "minItems": 1,
                    "maxItems": 5,
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "id": {"type": "STRING", "enum": allowed_ids},
                            "title": {"type": "STRING"},
                        },
                        "required": ["id", "title"],
                    },
                },
            },
            "required": ["quests"],
        }
        prompt = (
            "สร้างชุดเควสต์ตกปลารายวันเป็นภาษาไทย เลือก 1 ถึง 5 รายการจาก "
            f"ประเภทเหล่านี้: {json.dumps(allowed_ids, ensure_ascii=False)} "
            "ห้ามใช้ id ซ้ำ ตั้งชื่อ title สั้น กระชับ ไม่เกิน 32 ตัวอักษร "
            "ส่ง JSON ตาม schema เท่านั้น ห้ามสร้างกติกา ตัวเลขเป้าหมาย "
            "หรือน้ำหนักเอง เพราะเกมจะกำหนดจากเลเวลอุปกรณ์"
        )
        if force:
            previous = [
                {"id": quest["id"], "title": quest["title"]}
                for quest in previous_quests
            ]
            prompt += (
                " สร้างชุดใหม่ให้แตกต่างจากชุดก่อนหน้า และหลีกเลี่ยงชื่อเดิม: "
                f"{json.dumps(previous, ensure_ascii=False)}"
            )
        endpoint = f"{GEMINI_API_URL}/{GEMINI_MODEL}:generateContent"
        request_headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": os.environ["GEMINI_API_KEY"].strip(),
        }
        request_body = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseSchema": schema,
                "temperature": 0.8,
            },
        }
        response = None
        for attempt in range(GEMINI_MAX_ATTEMPTS):
            try:
                response = requests.post(
                    endpoint,
                    headers=request_headers,
                    json=request_body,
                    timeout=GEMINI_TIMEOUT,
                )
            except (requests.Timeout, requests.ConnectionError) as error:
                if attempt == GEMINI_MAX_ATTEMPTS - 1:
                    raise RuntimeError(
                        "เชื่อมต่อ Gemini ไม่ได้หลังลองใหม่ 3 ครั้ง"
                    ) from error
            else:
                if response.status_code not in GEMINI_RETRY_STATUSES:
                    break
                if attempt == GEMINI_MAX_ATTEMPTS - 1:
                    status = response.status_code
                    if status == 503:
                        message = "Gemini ไม่พร้อมให้บริการชั่วคราว (503)"
                    elif status == 429:
                        message = "Gemini จำกัดจำนวนคำขอ (429) กรุณารอสักครู่"
                    else:
                        message = f"Gemini ขัดข้องชั่วคราว (HTTP {status})"
                    raise RuntimeError(message)
            time.sleep(2 ** attempt)
        response.raise_for_status()
        try:
            text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            payload = json.loads(text)
            proposed = payload["quests"]
        except (KeyError, IndexError, TypeError, ValueError) as error:
            raise RuntimeError("Gemini ส่งข้อมูลเควสต์ที่อ่านไม่ได้") from error

        if not isinstance(proposed, list) or not 1 <= len(proposed) <= 5:
            raise RuntimeError("จำนวนเควสต์จาก Gemini ต้องอยู่ระหว่าง 1 ถึง 5")

        selected = []
        titles = {}
        for item in proposed:
            if not isinstance(item, dict):
                raise RuntimeError("รูปแบบเควสต์จาก Gemini ไม่ถูกต้อง")
            quest_id = item.get("id")
            title = item.get("title")
            if quest_id not in template_by_id or quest_id in titles:
                raise RuntimeError("ประเภทเควสต์จาก Gemini ซ้ำหรือไม่รองรับ")
            if not isinstance(title, str) or not title.strip():
                raise RuntimeError("ชื่อเควสต์จาก Gemini ว่างหรือไม่ถูกต้อง")
            selected.append(template_by_id[quest_id])
            titles[quest_id] = title.strip()[:32]

        if not apply:
            return True

        self.quest_date = today_key
        self.quests = self._build_quests(selected, today_key, titles)
        self.ai_checked = True
        self.ai_connected = True
        self._save_quest_data()
        return self.daily_quests(today)

    def mark_gemini_status(self, connected, today=None):
        """บันทึกผลตรวจการเชื่อม Gemini สำหรับเควสต์ของวันนี้"""
        today = today or date.today()
        self.daily_quests(today)
        self.ai_checked = True
        self.ai_connected = bool(connected)
        self._save_quest_data()

    def gemini_checked_today(self, today=None):
        """ระบุว่าวันนี้เคยลองเชื่อม Gemini แล้วหรือยัง"""
        today = today or date.today()
        self.daily_quests(today)
        return self.ai_checked

    def _build_quests(self, selected, today_key, titles=None):
        """สร้างข้อมูลที่เชื่อถือได้จากประเภทที่เลือกและเลเวลอุปกรณ์"""
        level_score = max(
            0, self.state.bait_level + self.state.rod_level - 2
        )
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
            quest = {
                **template,
                "date": today_key,
                "target": target,
                "min_weight": min_weight,
                "progress": 0,
                "reward": reward_base + target * 25 + level_score * 20,
                "claimed": False,
            }
            if titles and template["id"] in titles:
                quest["title"] = titles[template["id"]]
            quests.append(quest)
        return quests

    def _save_quest_data(self):
        self.state.quest_data = {
            "date": self.quest_date,
            "quests": [dict(quest) for quest in self.quests],
            "ai_checked": self.ai_checked,
            "ai_connected": self.ai_connected,
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
