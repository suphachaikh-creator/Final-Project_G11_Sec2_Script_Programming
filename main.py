"""จุดเริ่มโปรแกรมของเกม HOW_DO_YOU_FISH

รันด้วยคำสั่ง
    python main.py              เปิดโหมด Desktop GUI (ค่าเริ่มต้น)
    python main.py --cli        เปิดโหมด Terminal สำหรับเครื่องที่เปิดหน้าต่างไม่ได้

เกมจะดึงชนิดปลาจาก WoRMS และ Open Fisheries ให้อัตโนมัติ ถ้าเชื่อมต่อไม่ได้จะสลับไปใช้
ฐานข้อมูลสำรองใน data/fish_species.json แล้วแจ้งให้ผู้เล่นทราบ
"""

import os
import sys

os.environ["PYTHONIOENCODING"] = "utf-8"

# บังคับ UTF-8 ทั้งขาเข้าและขาออก ป้องกันภาษาไทยเพี้ยนบน Windows Console
for _stream in (sys.stdin, sys.stdout):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")


def run_cli():
    """โหมด Terminal เดิมจาก Sprint 1–2"""
    from src.cli import FishingCLI
    FishingCLI().run()


def run_gui():
    """โหมด Desktop GUI จาก Sprint 3

    เครื่องที่ไม่มี tkinter หรือไม่มีจอจะเปิดหน้าต่างไม่ได้ กรณีนั้นถอยไปใช้โหมด CLI
    แทนที่จะปล่อยให้โปรแกรมพัง
    """
    try:
        from src.gui.app import FishingApp
    except ImportError as error:
        print(f"เปิดหน้าต่างไม่ได้ ({type(error).__name__}) จะใช้โหมด Terminal แทน")
        return run_cli()

    import tkinter as tk
    try:
        FishingApp().mainloop()
    except tk.TclError as error:
        print(f"เปิดหน้าต่างไม่ได้ ({error}) จะใช้โหมด Terminal แทน")
        run_cli()


if __name__ == "__main__":
    if "--cli" in sys.argv:
        run_cli()
    else:
        run_gui()
