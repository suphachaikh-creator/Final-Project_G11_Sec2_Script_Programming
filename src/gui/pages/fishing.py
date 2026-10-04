"""หน้าตกปลาและมินิเกม QTE"""

import tkinter as tk
from tkinter import ttk

from src.fish import BRACKISH, FRESHWATER, MARINE
from src.gui.pages.common import BaseFrame, LOCATION_ICONS
from src.gui.presenter import FishingPresenter, location_label
from src.gui.theme import COLORS, PAD
from src.gui.widgets import Card, KeycapRow, TimerBar


class FishingFrame(BaseFrame):
    """หน้าตกปลา — มินิเกม QTE ที่เดินด้วย root.after()"""

    title = "ออกไปตกปลา"
    subtitle = "พิมพ์ตัวอักษรที่เรืองแสงให้ทันก่อนเวลาหมด พิมพ์ถูกจะได้เวลาเพิ่ม"

    def __init__(self, master, app):
        super().__init__(master, app)
        self.presenter = FishingPresenter(
            app.game, app.api, clock=app.clock, ai_agent=app.ai_agent
        )

        # ------------------------------------------------------ เลือกแหล่งน้ำ
        picker_card = Card(self, "📍  เลือกสถานที่", self.fonts)
        picker_card.pack(fill="x")

        self.location = tk.StringVar(value=FRESHWATER)
        row = ttk.Frame(picker_card, style="Card.TFrame")
        row.pack(anchor="w")
        for code in (FRESHWATER, MARINE, BRACKISH):
            ttk.Radiobutton(row, value=code, variable=self.location,
                            text=f"{LOCATION_ICONS[code]}  {location_label(code)}"
                            ).pack(side="left", padx=(0, 20))

        self.start_button = ttk.Button(picker_card, text="🎣  เริ่มตกปลา",
                                       style="Accent.TButton", command=self.start)
        self.start_button.pack(anchor="w", pady=(14, 0))

        # ---------------------------------------------------------- มินิเกม
        game_card = Card(self, "⚡  สู้กับปลา", self.fonts)
        game_card.pack(fill="x", pady=(PAD, 0))

        self.keycaps = KeycapRow(game_card, self.fonts)
        self.keycaps.pack(anchor="w", pady=(0, 14))

        self.timer_bar = TimerBar(game_card)
        self.timer_bar.pack(anchor="w")

        info = ttk.Frame(game_card, style="Card.TFrame")
        info.pack(fill="x", pady=(8, 0))
        self.timer = ttk.Label(info, style="Card.TLabel")
        self.timer.pack(side="left")

        self.message = ttk.Label(game_card, style="Success.TLabel",
                                 font=self.fonts["heading"])
        self.message.pack(anchor="w", pady=(14, 0))

    def start(self):
        """เริ่มรอบใหม่แล้วให้ตัวจับเวลาของ tkinter เดินต่อ"""
        self.presenter.start(self.location.get())
        self.message.config(text="พิมพ์ให้ทัน!", foreground=COLORS["text"])
        self.start_button.config(state="disabled")
        self.app.bind_keys(self.on_key)
        self.refresh()

    def on_key(self, event):
        """รับปุ่มจากคีย์บอร์ดส่งต่อให้ presenter ตัดสิน"""
        if self.presenter.press(event.char):
            self.refresh()

    def refresh(self):
        """อัปเดตหน้าจอจากสถานะปัจจุบัน"""
        game = self.presenter.minigame
        if game is not None:
            self.keycaps.show(game.targets, game.hit_count)
        self.timer.config(text=f"⏱  {self.presenter.timer_text()}")
        self.timer_bar.set(self.presenter.progress_ratio())
        if not self.presenter.is_running and game is not None:
            self.finish()

    def finish(self):
        """ปิดรอบและแสดงผล"""
        self.app.unbind_keys()
        game = self.presenter.minigame
        result = self.presenter.finish()
        won = bool(result and result["success"])
        self.message.config(text=self.presenter.result_text(),
                            foreground=COLORS["success"] if won else COLORS["danger"])
        self.keycaps.show(game.targets, game.total_targets)
        self.presenter.minigame = None
        self.start_button.config(state="normal")
        self.app.autosave()

    def on_show(self):
        self.message.config(text="")
        self.timer.config(text="")
        self.keycaps.clear()
        self.timer_bar.set(0)
        self.start_button.config(state="normal")
