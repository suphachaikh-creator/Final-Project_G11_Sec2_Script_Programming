"""วิดเจ็ตที่วาดเองเพื่อให้หน้าจอดูดีขึ้น (Sprint 3 — Full-Stack)

Tkinter ไม่มีการ์ดมุมมน แถบเวลาที่เปลี่ยนสี หรือปุ่มคีย์บอร์ดมาให้
ไฟล์นี้จึงวาดเองด้วย `Canvas` ทั้งหมด ยังคงเป็น **ชั้นวาดล้วนๆ**
ไม่มีกฎของเกมอยู่ในนี้แม้แต่บรรทัดเดียว
"""

import tkinter as tk
from tkinter import ttk

from src.gui.theme import COLORS, PAD, RADIUS, time_color


def rounded_rect(canvas, x1, y1, x2, y2, radius, **kwargs):
    """วาดสี่เหลี่ยมมุมมนบน Canvas

    Tkinter ไม่มีรูปทรงนี้ให้ จึงต้องประกอบจากเส้นโค้งเอง
    """
    radius = min(radius, abs(x2 - x1) / 2, abs(y2 - y1) / 2)
    points = [
        x1 + radius, y1, x2 - radius, y1, x2, y1,
        x2, y1 + radius, x2, y2 - radius, x2, y2,
        x2 - radius, y2, x1 + radius, y2, x1, y2,
        x1, y2 - radius, x1, y1 + radius, x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


class Card(ttk.Frame):
    """กล่องเนื้อหาพื้นอ่อนกว่าพื้นหลัง ใช้จัดกลุ่มข้อมูลให้อ่านง่าย"""

    def __init__(self, master, title=None, fonts=None, **kwargs):
        super().__init__(master, style="Card.TFrame", padding=PAD, **kwargs)
        if title:
            label = ttk.Label(self, text=title, style="Heading.TLabel")
            if fonts:
                label.configure(font=fonts["heading"])
            label.pack(anchor="w", pady=(0, 10))


class StatTile(ttk.Frame):
    """ตัวเลขใหญ่หนึ่งค่าพร้อมคำอธิบายใต้ตัวเลข"""

    def __init__(self, master, label, fonts, accent=False):
        super().__init__(master, style="Card.TFrame", padding=(PAD, 12))
        self.value = ttk.Label(self, text="-", style="Card.TLabel",
                               font=fonts["number"],
                               foreground=COLORS["gold"] if accent
                               else COLORS["text"])
        self.value.pack(anchor="w")
        ttk.Label(self, text=label, style="Muted.TLabel").pack(anchor="w")

    def set(self, text):
        """เปลี่ยนตัวเลขที่แสดง"""
        self.value.configure(text=str(text))


class TimerBar(tk.Canvas):
    """แถบเวลาที่เปลี่ยนสีตามเวลาที่เหลือ

    ใช้แทน `ttk.Progressbar` เพราะตัวนั้นเปลี่ยนสีระหว่างวิ่งไม่ได้
    """

    def __init__(self, master, width=420, height=14):
        super().__init__(master, width=width, height=height,
                         bg=COLORS["surface"], highlightthickness=0, bd=0)
        self.bar_width = width
        self.bar_height = height
        self.set(1.0)

    def set(self, ratio):
        """ตั้งค่าสัดส่วนเวลาที่เหลือ 0.0 - 1.0"""
        ratio = max(0.0, min(1.0, ratio))
        self.delete("all")
        rounded_rect(self, 0, 0, self.bar_width, self.bar_height,
                     self.bar_height / 2, fill=COLORS["surface_alt"], outline="")
        filled = self.bar_width * ratio
        if filled > 2:
            rounded_rect(self, 0, 0, filled, self.bar_height,
                         self.bar_height / 2, fill=time_color(ratio), outline="")


class KeycapRow(ttk.Frame):
    """แถวตัวอักษรของมินิเกม วาดเป็นปุ่มคีย์บอร์ด

    ตัวที่พิมพ์ไปแล้วจะจางลง ตัวที่ต้องกดตอนนี้จะเรืองสีหลัก
    ผู้เล่นจึงรู้ทันทีว่าต้องกดตัวไหนโดยไม่ต้องไล่อ่าน
    """

    CAP = 42
    GAP = 8

    def __init__(self, master, fonts):
        super().__init__(master, style="Card.TFrame")
        self.fonts = fonts
        self.canvas = tk.Canvas(self, height=self.CAP + 6, bg=COLORS["surface"],
                                highlightthickness=0, bd=0)
        self.canvas.pack(fill="x")

    def show(self, letters, done):
        """วาดตัวอักษรทั้งหมด โดย `done` คือจำนวนตัวที่พิมพ์ผ่านไปแล้ว"""
        self.canvas.delete("all")
        if not letters:
            return

        step = self.CAP + self.GAP
        self.canvas.configure(width=max(1, step * len(letters)))

        for index, letter in enumerate(letters):
            x = index * step
            if index < done:
                fill, text_color = COLORS["surface_alt"], COLORS["muted"]
            elif index == done:
                fill, text_color = COLORS["accent"], COLORS["bg"]
            else:
                fill, text_color = COLORS["border"], COLORS["text"]

            rounded_rect(self.canvas, x, 3, x + self.CAP, self.CAP + 3,
                         RADIUS, fill=fill, outline="")
            self.canvas.create_text(x + self.CAP / 2, (self.CAP + 6) / 2,
                                    text=letter.upper(), fill=text_color,
                                    font=self.fonts["mono"])

    def clear(self):
        """ล้างแถวตัวอักษร"""
        self.canvas.delete("all")
