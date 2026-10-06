"""คลาสและค่าร่วมของหน้าจอ GUI"""

from tkinter import ttk

from src.fish import BRACKISH, FRESHWATER, MARINE
from src.gui.theme import COLORS, PAD

LOCATION_ICONS = {
    FRESHWATER: "🏞",
    MARINE: "🌊",
    BRACKISH: "🏝",
}


class BaseFrame(ttk.Frame):
    """ส่วนที่ทุกหน้าจอใช้ร่วมกัน — หัวข้อด้านบน"""

    title = ""
    subtitle = ""

    def __init__(self, master, app):
        super().__init__(master, padding=(PAD + 8, PAD + 4))
        self.app = app
        self.fonts = app.fonts

        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, PAD))
        ttk.Label(header, text=self.title, style="Title.TLabel",
                  font=self.fonts["title"]).pack(anchor="w")
        if self.subtitle:
            ttk.Label(header, text=self.subtitle, foreground=COLORS["muted"],
                      font=self.fonts["small"]).pack(anchor="w", pady=(2, 0))

    def on_show(self):
        """เรียกทุกครั้งที่หน้าจอนี้ถูกเปิดขึ้นมา"""
