"""หน้าจอเกม แยกไฟล์ตามแต่ละหน้า"""

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