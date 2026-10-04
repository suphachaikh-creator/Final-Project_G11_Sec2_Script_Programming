"""หน้าคลังปลา ค้นหา กรอง เรียง และจัดการปลา"""

import tkinter as tk
from tkinter import ttk

from src.fish import BRACKISH, FRESHWATER, MARINE
from src.gui.pages.common import BaseFrame
from src.gui.presenter import (ALL_LOCATIONS, COLUMNS, SORTABLE,
                               InventoryPresenter, location_label)
from src.gui.theme import COLORS, PAD
from src.gui.widgets import Card, StatTile


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
