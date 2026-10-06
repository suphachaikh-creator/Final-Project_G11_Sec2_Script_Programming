"""หน้าเควสต์ตกปลา"""

import threading
from tkinter import ttk

from src.gui.pages.common import BaseFrame
from src.gui.theme import COLORS, PAD
from src.gui.widgets import Card

"""ตัวแปรควบคุมการทดสอบ Gemini API (เปิด True/ปิด False)"""
ENABLE_GEMINI_TEST_BUTTON = False


class QuestFrame(BaseFrame):
    """แสดงเควสต์ประจำวัน ความคืบหน้า และปุ่มรับรางวัล"""

    title = "เควสต์ตกปลา"
    subtitle = "ทำภารกิจให้สำเร็จเพื่อรับรางวัลประจำวัน"

    def __init__(self, master, app):
        super().__init__(master, app)

        ttk.Label(
            self, text="📜  เควสต์ประจำวัน", style="Heading.TLabel",
            font=self.fonts["heading"],
        ).pack(anchor="w", pady=(0, 8))
        self.gemini_toolbar = ttk.Frame(self)
        self.gemini_toolbar.pack(fill="x", pady=(0, 8))
        self.gemini_status = ttk.Label(
            self.gemini_toolbar, style="Muted.TLabel", wraplength=430,
        )
        self.gemini_status.pack(side="left", anchor="w")
        self._gemini_request_running = False
        if ENABLE_GEMINI_TEST_BUTTON:
            self.gemini_test_button = ttk.Button(
                self.gemini_toolbar, text="ทดสอบ API / สร้างเควสต์ใหม่",
                command=self.test_gemini_api,
            )
            self.gemini_test_button.pack(side="right", anchor="e")

        self.quest_rows = ttk.Frame(self)
        self.quest_rows.pack(fill="x")

        self.info_card = Card(self, "🤖  ผู้ช่วยตกปลาอัจฉริยะ", self.fonts)
        self.info_card.pack(fill="x", pady=(PAD, 0))
        ttk.Label(
            self.info_card,
            text=("จำนวนและความยากของเควสต์ปรับตามเลเวลเหยื่อและคันเบ็ด "
                  "เควสต์ในวันเดียวกันจะไม่มีเป้าหมายซ้ำกัน"),
            style="Card.TLabel", wraplength=650, justify="left",
        ).pack(anchor="w")

    def on_show(self):
        self.refresh_quests()
        self.check_ai_connection()

    def refresh_quests(self):
        """สร้างแถวแสดงผลใหม่จากเควสต์ปัจจุบันของเอเจนต์"""
        for row in self.quest_rows.winfo_children():
            row.destroy()

        saved_date = self.app.game.quest_data.get("date")
        quests = self.app.ai_agent.daily_quests()
        if saved_date != quests[0]["date"]:
            self.app.autosave()
        for quest in quests:
            self._add_quest_row(quest)

    def check_ai_connection(self):
        """ตรวจ AI เมื่อเปิดหน้า แล้วสร้างเควสต์จาก API หรือ fallback"""
        agent = self.app.ai_agent
        if agent.gemini_checked_today():
            if agent.ai_connected:
                text = "เชื่อม Gemini API แล้ว วันนี้ใช้เควสต์จาก Gemini"
            else:
                text = "ไม่ได้เชื่อม Gemini API วันนี้ใช้เควสต์จาก AI ในเกม"
            self.gemini_status.config(text=text)
            return

        if not agent.gemini_configured:
            agent.mark_gemini_status(False)
            self.app.autosave()
            text = "ไม่ได้เชื่อม Gemini API · ใช้ AI ในเกมสร้างเควสต์แทน"
            self.gemini_status.config(text=text)
            return

        if self._gemini_request_running:
            return
        self._gemini_request_running = True
        self.gemini_status.config(text="กำลังตรวจการเชื่อมต่อ Gemini API...")
        worker = threading.Thread(target=self._generate_gemini_quests,
                                  daemon=True)
        worker.start()

    def _generate_gemini_quests(self):
        """เรียก API ในเธรดเบื้องหลัง ไม่ให้หน้าต่างเกมค้าง"""
        try:
            self.app.ai_agent.generate_gemini_quests()
            error = None
        except Exception as caught_error:  # API/network errors use local quests
            self.app.ai_agent.mark_gemini_status(False)
            error = str(caught_error)
        self.after(0, lambda: self._finish_gemini_request(error))

    def _finish_gemini_request(self, error):
        self._gemini_request_running = False
        self.app.autosave()
        self.refresh_quests()
        if error:
            text = f"เชื่อม Gemini API ไม่สำเร็จ · ใช้ AI ในเกมแทน ({error})"
        else:
            text = "เชื่อม Gemini API สำเร็จ · Gemini สร้างเควสต์วันนี้แล้ว"
        self.gemini_status.config(text=text)

    def test_gemini_api(self):
        """ทดสอบ Gemini และแทนชุดเควสต์เดิมเมื่อสร้างชุดใหม่สำเร็จ"""
        if self._gemini_request_running:
            self.gemini_status.config(text="กำลังตรวจ Gemini อยู่ กรุณารอสักครู่")
            return
        self._gemini_request_running = True
        self.gemini_test_button.config(state="disabled")
        self.gemini_status.config(text="กำลังทดสอบ Gemini API...")
        worker = threading.Thread(target=self._run_gemini_test, daemon=True)
        worker.start()

    def _run_gemini_test(self):
        try:
            self.app.ai_agent.generate_gemini_quests(force=True)
            error = None
        except Exception as caught_error:  # display a concise test result
            error = str(caught_error)
            self.app.ai_agent.generate_local_quests()
        self.after(0, lambda: self._finish_gemini_test(error))

    def _finish_gemini_test(self, error):
        self._gemini_request_running = False
        self.gemini_test_button.config(state="normal")
        if error:
            self.app.autosave()
            self.refresh_quests()
            text = f"Gemini ใช้ไม่ได้ · สุ่มชุดใหม่จาก AI ในเกมแทน ({error})"
        else:
            self.app.autosave()
            self.refresh_quests()
            text = "Gemini สร้างและแสดงชุดเควสต์ใหม่แล้ว"
        self.gemini_status.config(text=text)

    def _add_quest_row(self, quest):
        card = Card(
            self.quest_rows, quest["title"], self.fonts,
        )
        card.pack(fill="x", pady=(0, 8))
        row = ttk.Frame(card, style="Card.TFrame")
        row.pack(fill="x")
        row.columnconfigure(0, weight=1)

        ttk.Label(
            row, text=f"รางวัล  💰 ${quest['reward']}",
            style="Gold.TLabel", font=self.fonts["small"],
        ).grid(row=0, column=1, sticky="e", padx=(PAD, 0))

        ttk.Label(
            row, text=self.app.ai_agent.quest_description(quest),
            style="Muted.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(3, 0))
        progress_text = ttk.Label(
            row, text=f"{quest['progress']} / {quest['target']} ตัว",
            style="Card.TLabel",
        )
        progress_text.grid(row=2, column=0, sticky="w", pady=(6, 0))

        ttk.Style(self).configure(
            "Quest.Horizontal.TProgressbar",
            troughcolor=COLORS["surface_alt"],
            background=COLORS["accent"],
            bordercolor=COLORS["surface"],
            lightcolor=COLORS["accent"],
            darkcolor=COLORS["accent"],
            thickness=12,
        )
        progress_bar = ttk.Progressbar(
            row, maximum=quest["target"], value=quest["progress"],
            mode="determinate", style="Quest.Horizontal.TProgressbar",
        )
        progress_bar.grid(row=3, column=0, sticky="ew", pady=(4, 0))

        completed = quest["progress"] >= quest["target"]
        if quest["claimed"]:
            button_text = "รับแล้ว"
            button_state = "disabled"
        elif completed:
            button_text = "รับรางวัล"
            button_state = "normal"
        else:
            button_text = "ยังไม่สำเร็จ"
            button_state = "disabled"
        ttk.Button(
            row, text=button_text, state=button_state,
            command=lambda quest_id=quest["id"]: self.claim_reward(quest_id),
        ).grid(row=1, column=1, rowspan=3, sticky="e", padx=(PAD, 0))

    def claim_reward(self, quest_id):
        """รับรางวัลของเควสต์ที่เลือกและอัปเดตเงินบนแถบเมนู"""
        reward = self.app.ai_agent.claim_reward(quest_id)
        if reward:
            self.app.autosave()
        self.refresh_quests()
