"""หน้าจอเกม แยกไฟล์ตามแต่ละหน้า

ไฟล์ในโฟลเดอร์นี้ทำหน้าที่ **วาดอย่างเดียว** การตัดสินใจทุกอย่างถามจาก `presenter.py`
ถ้าเห็นเงื่อนไข if ที่เป็นกฎของเกมอยู่ในไฟล์เหล่านี้ แปลว่าวางผิดที่แล้ว
สีและฟอนต์อยู่ใน `theme.py` ส่วนวิดเจ็ตที่วาดเองอยู่ใน `widgets.py`
"""

from src.gui.pages.dashboard import DashboardFrame
from src.gui.pages.fishing import FishingFrame
from src.gui.pages.inventory import InventoryFrame
from src.gui.pages.quest import QuestFrame
from src.gui.pages.shop import ShopFrame

__all__ = [
    "DashboardFrame",
    "FishingFrame",
    "InventoryFrame",
    "QuestFrame",
    "ShopFrame",
]
