"""หน้าจอทั้ง 4 หน้าของเกม (Sprint 3 — Full-Stack)

ไฟล์นี้ทำหน้าที่ **วาดอย่างเดียว** การตัดสินใจทุกอย่างถามจาก `presenter.py`
ถ้าเห็นเงื่อนไข if ที่เป็นกฎของเกมอยู่ในไฟล์นี้ แปลว่าวางผิดที่แล้ว
สีและฟอนต์อยู่ใน `theme.py` ส่วนวิดเจ็ตที่วาดเองอยู่ใน `widgets.py`
"""

import tkinter as tk
from tkinter import ttk

from src.fish import BRACKISH, FRESHWATER, MARINE
from src.gui.presenter import (ALL_LOCATIONS, COLUMNS, SORTABLE,
                               DashboardPresenter, FishingPresenter,
                               InventoryPresenter, ShopPresenter,
                               location_label)
from src.gui.theme import COLORS, PAD
from src.gui.widgets import Card, KeycapRow, StatTile, TimerBar

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


class FishingFrame(BaseFrame):
    """หน้าตกปลา — มินิเกม QTE ที่เดินด้วย root.after()"""

    title = "ออกไปตกปลา"
    subtitle = "พิมพ์ตัวอักษรที่เรืองแสงให้ทันก่อนเวลาหมด พิมพ์ถูกจะได้เวลาเพิ่ม"

    def __init__(self, master, app):
        super().__init__(master, app)
        self.presenter = FishingPresenter(app.game, app.api, clock=app.clock)

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


class ShopFrame(BaseFrame):
    """หน้าร้านค้า — ปุ่มซื้อจะถูกปิดเองเมื่อเงินไม่พอ"""

    title = "ร้านค้า"
    subtitle = "เหยื่อเลเวลสูงได้ปลาตัวใหญ่ขึ้น คันเบ็ดเลเวลสูงได้เวลาสู้ปลามากขึ้น"

    def __init__(self, master, app):
        super().__init__(master, app)
        self.presenter = ShopPresenter(app.game)

        money_card = Card(self)
        money_card.pack(fill="x")
        self.money = ttk.Label(money_card, style="Gold.TLabel",
                               font=self.fonts["number"])
        self.money.pack(anchor="w")
        ttk.Label(money_card, text="เงินคงเหลือ",
                  style="Muted.TLabel").pack(anchor="w")

        self.buttons = {}
        self.costs = {}
        for item in self.presenter.items():
            card = Card(self)
            card.pack(fill="x", pady=(PAD, 0))

            label = ttk.Label(card, text=item["label"], style="Card.TLabel",
                              font=self.fonts["heading"])
            label.pack(anchor="w")
            cost = ttk.Label(card, style="Muted.TLabel")
            cost.pack(anchor="w", pady=(2, 10))

            button = ttk.Button(card, text="ซื้อ", style="Accent.TButton",
                                command=lambda key=item["key"]: self.buy(key))
            button.pack(anchor="w")
            self.buttons[item["key"]] = (button, label)
            self.costs[item["key"]] = cost

        self.message = ttk.Label(self, foreground=COLORS["danger"])
        self.message.pack(anchor="w", pady=(PAD, 0))

    def buy(self, key):
        ok, text = self.presenter.buy(key)
        self.message.config(
            text=text, foreground=COLORS["success"] if ok else COLORS["danger"])
        self.on_show()
        if ok:
            self.app.autosave()

    def on_show(self):
        self.money.config(text=f"${self.app.game.money}")
        for item in self.presenter.items():
            button, label = self.buttons[item["key"]]
            label.config(text=item["label"])
            self.costs[item["key"]].config(text=f"ราคา ${item['cost']}")
            button.config(state="normal" if item["enabled"] else "disabled",
                          text="ซื้อ" if item["enabled"] else "เงินไม่พอ")


class InventoryFrame(BaseFrame):
    """หน้าคลังสินค้า — ตาราง Treeview พร้อมค้นหา กรอง และเรียงลำดับ"""

    title = "คลังสินค้า"
    subtitle = ("คลิกหัวคอลัมน์เพื่อเรียงลำดับ · "
                "คลิกแถวเพื่อเลือกปลาแล้วขายทีละตัวหรือขายยกชนิด")

    def __init__(self, master, app):
        super().__init__(master, app)
        self.presenter = InventoryPresenter(app.game)

        # ------------------------------------------------------- แถบเครื่องมือ
        tools = Card(self)
        tools.pack(fill="x")
        row = ttk.Frame(tools, style="Card.TFrame")
        row.pack(fill="x")

        ttk.Label(row, text="🔍", style="Card.TLabel").pack(side="left")
        self.keyword = tk.StringVar()
        entry = ttk.Entry(row, textvariable=self.keyword, width=24)
        entry.pack(side="left", padx=(6, PAD))
        entry.bind("<KeyRelease>", lambda event: self.refresh())

        ttk.Label(row, text="แหล่งน้ำ", style="Muted.TLabel").pack(side="left")
        self.choices = [ALL_LOCATIONS, FRESHWATER, MARINE, BRACKISH]
        self.location = tk.StringVar()
        box = ttk.Combobox(row, textvariable=self.location, width=18,
                           state="readonly", values=[
                               "ทั้งหมด" if code == ALL_LOCATIONS
                               else location_label(code) for code in self.choices])
        box.pack(side="left", padx=(8, 0))
        box.current(0)
        box.bind("<<ComboboxSelected>>",
                 lambda event: self.pick_location(self.choices[box.current()]))

        ttk.Label(row, text="ชื่อใหม่", style="Muted.TLabel").pack(
            side="left", padx=(PAD, 0))
        self.new_name = tk.StringVar()
        name_entry = ttk.Entry(row, textvariable=self.new_name, width=16)
        name_entry.pack(side="left", padx=(6, 6))
        name_entry.bind("<Return>", lambda event: self.rename())
        self.rename_button = ttk.Button(row, text="เปลี่ยนชื่อ",
                                        command=self.rename)
        self.rename_button.pack(side="left")

        self.selection_label = ttk.Label(row, style="Muted.TLabel")
        self.selection_label.pack(side="right")

        # ------------------------------------------------------------- ตาราง
        table_card = Card(self)
        table_card.pack(fill="both", expand=True, pady=(PAD, 0))

        wrap = ttk.Frame(table_card, style="Card.TFrame")
        wrap.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(wrap, columns=COLUMNS, show="headings", height=10)
        scroll = ttk.Scrollbar(wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        for key in COLUMNS:
            self.tree.heading(key, command=lambda name=key: self.sort_by(name))
            self.tree.column(key, width=170, anchor="w")
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.tree.tag_configure("odd", background=COLORS["surface_alt"])
        self.tree.bind("<<TreeviewSelect>>",
                       lambda event: self.update_sell_buttons())

        # ---------------------------------------------------------- ปุ่มขาย
        sell_row = ttk.Frame(table_card, style="Card.TFrame")
        sell_row.pack(fill="x", pady=(14, 0))

        self.sell_one_button = ttk.Button(
            sell_row, text="ขายตัวที่เลือก", style="Accent.TButton",
            command=self.sell_one)
        self.sell_one_button.pack(side="left")

        self.sell_species_button = ttk.Button(
            sell_row, text="ขายทั้งชนิดนี้", command=self.sell_species)
        self.sell_species_button.pack(side="left", padx=(10, 0))

        self.keep_button = ttk.Button(
            sell_row, text="เก็บไว้ไม่ขาย", command=self.toggle_keep)
        self.keep_button.pack(side="left", padx=(10, 0))

        ttk.Button(sell_row, text="💰  ขายปลาทั้งหมด",
                   command=self.sell).pack(side="right")

        # -------------------------------------------------------------- สถิติ
        stats_row = ttk.Frame(self)
        stats_row.pack(fill="x", pady=(PAD, 0))
        self.stats = {}
        for index, (key, label) in enumerate((
                ("count", "จำนวนปลา"), ("total", "มูลค่ารวม"),
                ("average", "น้ำหนักเฉลี่ย"), ("heaviest", "ตัวที่หนักที่สุด"))):
            tile = StatTile(stats_row, label, self.fonts, accent=(key == "total"))
            tile.grid(row=0, column=index, sticky="ew", padx=(0, 10))
            stats_row.columnconfigure(index, weight=1)
            self.stats[key] = tile

        self.message = ttk.Label(self, foreground=COLORS["success"])
        self.message.pack(anchor="w", pady=(10, 0))

    def pick_location(self, code):
        self.presenter.location_filter = code
        self.refresh()

    def sort_by(self, key):
        """คลิกหัวคอลัมน์เพื่อเรียงลำดับ คอลัมน์ที่เรียงไม่ได้จะไม่ทำอะไร"""
        if key not in SORTABLE:
            return
        self.presenter.toggle_sort(key)
        self.refresh()

    def selected_index(self):
        """ลำดับแถวที่ผู้เล่นเลือกอยู่ คืน None เมื่อยังไม่ได้เลือก"""
        selection = self.tree.selection()
        if not selection:
            return None
        return self.tree.index(selection[0])

    def update_sell_buttons(self):
        """เปิด-ปิดปุ่มขายตามว่าเลือกแถวไว้หรือยัง"""
        index = self.selected_index()
        fish = self.presenter.fish_at(index)
        count = self.presenter.species_count_at(index)

        state = "normal" if fish else "disabled"
        self.sell_one_button.config(state=state)
        self.rename_button.config(state=state)
        self.keep_button.config(
            state=state, text=self.presenter.keep_label_at(index))
        self.sell_species_button.config(
            state=state,
            text=f"ขายทั้งชนิดนี้ ({count} ตัว)" if fish else "ขายทั้งชนิดนี้")
        self.selection_label.config(
            text=f"เลือก {fish.name}" if fish else "คลิกแถวเพื่อเลือกปลา")

    def rename(self):
        """ตั้งชื่อเล่นให้ปลาที่เลือก"""
        message = self.presenter.rename_at(self.selected_index(),
                                           self.new_name.get())
        self.new_name.set("")
        self.after_change(message)

    def toggle_keep(self):
        """สลับสถานะเก็บไว้ไม่ขายของปลาที่เลือก"""
        self.after_change(
            self.presenter.toggle_keep_at(self.selected_index()))

    def sell_one(self):
        """ขายปลาตัวที่เลือกตัวเดียว"""
        self.after_change(self.presenter.sell_one(self.selected_index()))

    def sell_species(self):
        """ขายปลาทุกตัวที่เป็นชนิดเดียวกับตัวที่เลือก"""
        self.after_change(
            self.presenter.sell_species_at(self.selected_index()))

    def sell(self):
        """ขายปลาทั้งกระเป๋า"""
        self.after_change(self.presenter.sell_all())

    def after_change(self, message):
        """งานที่ต้องทำเหมือนกันทุกครั้งที่กระเป๋าเปลี่ยน"""
        self.message.config(text=message)
        self.refresh()
        self.app.autosave()

    def refresh(self):
        self.presenter.keyword = self.keyword.get()
        for key in COLUMNS:
            self.tree.heading(key, text=self.presenter.heading_text(key))

        self.tree.delete(*self.tree.get_children())
        for index, row in enumerate(self.presenter.visible_rows()):
            self.tree.insert("", "end", values=row,
                             tags=("odd",) if index % 2 else ())

        stats = self.app.game.summary()
        self.stats["count"].set(stats["count"])
        self.stats["total"].set(f"${stats['total_price']}")
        self.stats["average"].set(f"{stats['average_weight']} กก.")
        heaviest = stats["heaviest"]
        self.stats["heaviest"].set(heaviest.name if heaviest else "-")
        self.update_sell_buttons()

    def on_show(self):
        self.message.config(text="")
        self.refresh()
