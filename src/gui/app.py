"""หน้าต่างหลักของเกม (Sprint 3 — Full-Stack)

`FishingApp` ถือสถานะเกม สลับเฟรม และเดินตัวจับเวลาด้วย `root.after()`
ตรรกะของเกมทั้งหมดยังอยู่ที่ชั้นเดิมจาก Sprint 1-2 ไฟล์นี้ไม่ได้ตัดสินใจอะไรเอง

หน้าต่างแบ่งเป็นสองส่วน — แถบเมนูด้านซ้ายที่อยู่ตลอดเวลา และพื้นที่เนื้อหาด้านขวา
ที่สลับเฟรมไปมา ทำแบบนี้แทนปุ่มนำทางด้านล่างของทุกหน้า เพราะผู้เล่นจะเห็นตลอดว่า
ตอนนี้อยู่หน้าไหนและไปหน้าไหนได้บ้าง
"""

import tkinter as tk
from tkinter import ttk

from src.ai_fishing import AIFishingAgent
from src.gui.presenter import TkClock
from src.gui.species_loader import SpeciesLoader
from src.gui.theme import COLORS, apply_theme
from src.save_manager import SaveManager

TICK_MS = 100
WINDOW_SIZE = "1020x700"
MIN_SIZE = (900, 640)

NAV_ITEMS = (
    ("dashboard", "🏠   หน้าแรก"),
    ("fishing", "🎣   ออกไปตกปลา"),
    ("quests", "📜   เควสต์ตกปลา"),
    ("shop", "🛒   ร้านค้า"),
    ("inventory", "🎒   คลังสินค้า"),
)


class FishingApp(tk.Tk):
    """หน้าต่างเกมทั้งหมด"""

    def __init__(self, state=None, api=None, saver=None):
        super().__init__()
        self.title("HOW DO YOU FISH")
        self.geometry(WINDOW_SIZE)
        self.minsize(*MIN_SIZE)
        self.fonts = apply_theme(self)

        self.saver = saver or SaveManager()
        self.state_data = state or self.saver.load_or_new()
        self.ai_agent = AIFishingAgent(self.state_data)
        # ห่อ API ไว้ด้วยตัวโหลดเบื้องหลัง ไม่งั้นการจับปลาครั้งแรกจะทำให้
        # หน้าต่างค้างราว 34 วินาทีระหว่างรอ WoRMS กับ Open Fisheries
        self.api = api or SpeciesLoader()
        self.clock = TkClock(TICK_MS)
        self._key_handler = None
        self._tick_id = None

        self.current = None
        self.nav_buttons = {}
        content = self._build_shell()

        # import ที่นี่เพื่อเลี่ยงการ import วนระหว่างสองไฟล์
        from src.gui.pages import (DashboardFrame, FishingFrame,
                                   InventoryFrame, QuestFrame, ShopFrame)

        self.frames = {}
        for name, frame_class in (("dashboard", DashboardFrame),
                                  ("fishing", FishingFrame),
                                  ("quests", QuestFrame),
                                  ("shop", ShopFrame),
                                  ("inventory", InventoryFrame)):
            frame = frame_class(content, self)
            frame.place(relwidth=1, relheight=1)
            self.frames[name] = frame

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.show_frame("dashboard")
        self.start_loading()
        self._tick_id = self.after(TICK_MS, self.tick)

    # ------------------------------------------------------------ โครงหน้าต่าง
    def _build_shell(self):
        """สร้างแถบเมนูซ้ายกับพื้นที่เนื้อหาขวา คืนค่าพื้นที่เนื้อหา"""
        sidebar = ttk.Frame(self, style="Sidebar.TFrame", width=232)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        brand = ttk.Frame(sidebar, style="Sidebar.TFrame",
                          padding=(20, 26, 20, 18))
        brand.pack(fill="x")
        ttk.Label(brand, text="🎣", background=COLORS["sidebar"],
                  font=(self.fonts["title"][0], 26)).pack(anchor="w")
        ttk.Label(brand, text="HOW DO YOU FISH", background=COLORS["sidebar"],
                  foreground=COLORS["text"],
                  font=(self.fonts["body"][0], 12, "bold")).pack(anchor="w",
                                                                 pady=(6, 0))
        ttk.Label(brand, text="CP352301 · Group 11", background=COLORS["sidebar"],
                  foreground=COLORS["muted"],
                  font=self.fonts["small"]).pack(anchor="w")

        for name, label in NAV_ITEMS:
            button = ttk.Button(sidebar, text=label, style="Nav.TButton",
                                command=lambda key=name: self.show_frame(key))
            button.pack(fill="x", padx=12, pady=2)
            self.nav_buttons[name] = button

        # แถบล่างของเมนู แสดงเงินและจำนวนปลาให้เห็นตลอดโดยไม่ต้องกลับหน้าแรก
        footer = ttk.Frame(sidebar, style="Sidebar.TFrame", padding=(20, 16))
        footer.pack(side="bottom", fill="x")
        self.money_label = ttk.Label(footer, background=COLORS["sidebar"],
                                     foreground=COLORS["gold"],
                                     font=(self.fonts["body"][0], 15, "bold"))
        self.money_label.pack(anchor="w")
        self.bag_label = ttk.Label(footer, background=COLORS["sidebar"],
                                   foreground=COLORS["muted"],
                                   font=self.fonts["small"])
        self.bag_label.pack(anchor="w")

        content = ttk.Frame(self)
        content.pack(side="left", fill="both", expand=True)
        return content

    def autosave(self):
        """บันทึกทันทีที่สถานะเปลี่ยน

        ข้อกำหนดของสปรินต์คือข้อมูลในหน่วยความจำต้องตรงกับไฟล์ตลอดเวลา
        ถ้าเซฟแค่ตอนปิดหน้าต่าง ไฟดับหรือปิดผิดปกติแล้วความคืบหน้าจะหาย
        """
        self.saver.save(self.state_data)
        self.refresh_sidebar()
        return self.saver.last_error is None

    def refresh_sidebar(self):
        """อัปเดตเงินและจำนวนปลาบนแถบเมนู เรียกทุกครั้งที่ค่าเปลี่ยน"""
        self.money_label.config(text=f"${self.state_data.money}")
        self.bag_label.config(
            text=f"ปลาในกระเป๋า {len(self.state_data.inventory)} ตัว")

    @property
    def game(self):
        """สถานะเกม ใช้ชื่อ game ไม่ใช่ state เพราะ `tk.Tk.state()`
        เป็นเมธอดของ tkinter อยู่แล้ว ถ้าตั้งชื่อทับจะไปบังของเดิม
        """
        return self.state_data

    # ------------------------------------------------------------ การสลับหน้า
    def show_frame(self, name):
        """สลับไปยังหน้าจอที่ระบุ แล้วให้หน้านั้นรีเฟรชตัวเอง"""
        frame = self.frames[name]
        frame.tkraise()
        frame.on_show()

        self.current = name
        for key, button in self.nav_buttons.items():
            button.configure(style="NavActive.TButton" if key == name
                             else "Nav.TButton")
        self.refresh_sidebar()
        return frame

    def start_loading(self):
        """เริ่มโหลดข้อมูลปลาเบื้องหลัง แล้วคอยรีเฟรชหน้าแรกจนกว่าจะเสร็จ"""
        starter = getattr(self.api, "start", None)
        if not callable(starter):
            return
        starter()
        self._watch_loading()

    def _watch_loading(self):
        """ถามสถานะการโหลดเป็นระยะ พอเสร็จแล้วอัปเดตหน้าจอครั้งสุดท้าย"""
        if self.current == "dashboard":
            self.frames["dashboard"].refresh_status()
        if getattr(self.api, "is_complete", True):
            return
        self.after(500, self._watch_loading)

    def bind_keys(self, handler):
        """ให้หน้าจอที่กำลังเล่นมินิเกมรับปุ่มจากคีย์บอร์ด"""
        self._key_handler = handler
        self.bind("<Key>", handler)

    def unbind_keys(self):
        """เลิกรับปุ่มเมื่อจบรอบ"""
        if self._key_handler is not None:
            self.unbind("<Key>")
            self._key_handler = None

    def tick(self):
        """จังหวะเวลาของเกม เดินนาฬิกาแล้วให้หน้าตกปลารีเฟรช"""
        self.clock.tick()
        fishing = self.frames["fishing"]
        if fishing.presenter.minigame is not None:
            fishing.refresh()
        self._tick_id = self.after(TICK_MS, self.tick)

    def on_close(self):
        """บันทึกเกมก่อนปิดหน้าต่างเสมอ ผู้เล่นจึงไม่เสียความคืบหน้า"""
        self.saver.save(self.state_data)

        # ยกเลิกตัวจับเวลาที่ค้างอยู่ก่อนทำลายหน้าต่าง
        # ถ้าไม่ยกเลิก callback จะยิงหลังหน้าต่างหายไปแล้วและโยน TclError
        if self._tick_id is not None:
            self.after_cancel(self._tick_id)
            self._tick_id = None
        self.destroy()


def main():
    """จุดเริ่มของโหมด GUI"""
    FishingApp().mainloop()


if __name__ == "__main__":
    main()
