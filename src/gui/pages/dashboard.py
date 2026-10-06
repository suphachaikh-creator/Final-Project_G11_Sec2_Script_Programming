"""หน้าแรกและสถานะข้อมูลของเกม"""

import webbrowser
from tkinter import ttk

from src.gui.pages.common import BaseFrame
from src.gui.presenter import DashboardPresenter
from src.gui.theme import PAD
from src.gui.widgets import Card, StatTile


class DashboardFrame(BaseFrame):
    """หน้าแรก — สถานะผู้เล่นและแหล่งข้อมูล"""

    title = "HOW DO YOU FISH"
    subtitle = "เกมจำลองการตกปลา · ข้อมูลชนิดปลาจาก WoRMS และ Open Fisheries"

    def __init__(self, master, app):
        super().__init__(master, app)
        self.presenter = DashboardPresenter(app.game, app.api, catch_log=app.catch_log,
                                            updates=app.updates)

        # ---------------------------------------------------- แถวตัวเลขสถานะ
        tiles = ttk.Frame(self)
        tiles.pack(fill="x")
        self.tiles = {}
        for index, (key, label, accent) in enumerate((
                ("money", "เงินคงเหลือ", True),
                ("bait", "เลเวลเหยื่อ", False),
                ("rod", "เลเวลคันเบ็ด", False),
                ("fish", "ปลาในกระเป๋า", False))):
            tile = StatTile(tiles, label, self.fonts, accent=accent)
            tile.grid(row=0, column=index, sticky="ew", padx=(0, 10))
            tiles.columnconfigure(index, weight=1)
            self.tiles[key] = tile

        # ------------------------------------------------- สถิติตลอดการเล่น
        history_card = Card(self, "📊  สถิติตลอดการเล่น", self.fonts)
        history_card.pack(fill="x", pady=(PAD, 0))
        self.history_label = ttk.Label(history_card, style="Card.TLabel",
                                       justify="left", wraplength=650)
        self.history_label.pack(anchor="w")

        # -------------------------------------------------------- สถานะข้อมูล
        status_card = Card(self, "🛰  แหล่งข้อมูล", self.fonts)
        status_card.pack(fill="x", pady=(PAD, 0))
        self.api_label = ttk.Label(status_card, style="Card.TLabel")
        self.api_label.pack(anchor="w")

        # -------------------------------------------------------- เวอร์ชันของเกม
        version_card = Card(self, "🔄  เวอร์ชันของเกม", self.fonts)
        version_card.pack(fill="x", pady=(PAD, 0))
        self.version_label = ttk.Label(version_card, style="Card.TLabel",
                                       justify="left", wraplength=650)
        self.version_label.pack(anchor="w")
        self.download_button = ttk.Button(version_card, text="📥  ไปหน้าดาวน์โหลดเวอร์ชันใหม่",
                                          style="Accent.TButton",
                                          command=self.open_download_page)

    def on_show(self):
        state = self.app.game
        self.tiles["money"].set(f"${state.money}")
        self.tiles["bait"].set(state.bait_level)
        self.tiles["rod"].set(state.rod_level)
        self.tiles["fish"].set(len(state.inventory))
        self.history_label.config(text="\n".join(self.presenter.history_lines()))

        self.refresh_status()

    def refresh_status(self):
        """อัปเดตสถานะแหล่งข้อมูลและเวอร์ชัน ใช้ตอนงานเบื้องหลังเสร็จ"""
        self.api_label.config(text=self.presenter.api_status())
        self.version_label.config(text=self.presenter.version_text())
        if self.presenter.can_download_update():
            self.download_button.pack(anchor="w", pady=(10, 0))
        else:
            self.download_button.pack_forget()

    def open_download_page(self):
        """เปิดหน้า Releases ในเบราว์เซอร์ ผู้เล่นดาวน์โหลดเอง ไม่เขียนทับเกมอัตโนมัติ"""
        webbrowser.open(self.app.updates.url)
