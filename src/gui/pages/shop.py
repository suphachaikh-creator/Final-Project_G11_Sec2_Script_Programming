"""หน้าร้านค้าและการอัปเกรดอุปกรณ์"""

from tkinter import ttk

from src.gui.pages.common import BaseFrame
from src.gui.presenter import ShopPresenter
from src.gui.theme import COLORS, PAD
from src.gui.widgets import Card


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

