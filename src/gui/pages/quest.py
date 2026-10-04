"""หน้าเควสต์ตกปลา"""

from tkinter import ttk

from src.gui.pages.common import BaseFrame
from src.gui.theme import COLORS, PAD
from src.gui.widgets import Card


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
