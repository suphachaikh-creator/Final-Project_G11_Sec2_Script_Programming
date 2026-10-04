"""นำเข้าคลาสหน้าจอจากโมดูลรายหน้า (เพื่อรองรับ import เดิม)"""

from src.gui.pages import (DashboardFrame, FishingFrame, InventoryFrame,
                           QuestFrame, ShopFrame)

__all__ = [
    "DashboardFrame",
    "FishingFrame",
    "InventoryFrame",
    "QuestFrame",
    "ShopFrame",
]