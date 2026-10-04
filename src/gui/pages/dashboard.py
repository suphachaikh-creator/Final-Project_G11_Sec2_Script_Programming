"""หน้าแรกและสถานะข้อมูลของเกม"""

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
        self.presenter = DashboardPresenter(app.game, app.api)

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

        # -------------------------------------------------------- สถานะข้อมูล
        status_card = Card(self, "🛰  แหล่งข้อมูล", self.fonts)
        status_card.pack(fill="x", pady=(PAD, 0))
        self.api_label = ttk.Label(status_card, style="Card.TLabel")
        self.api_label.pack(anchor="w")

    def on_show(self):
        state = self.app.game
        self.tiles["money"].set(f"${state.money}")
        self.tiles["bait"].set(state.bait_level)
        self.tiles["rod"].set(state.rod_level)
        self.tiles["fish"].set(len(state.inventory))

        self.refresh_status()

    def refresh_status(self):
        """อัปเดตแค่บรรทัดสถานะแหล่งข้อมูล ใช้ตอนโหลดเบื้องหลังเสร็จ"""
        self.api_label.config(text=self.presenter.api_status())

