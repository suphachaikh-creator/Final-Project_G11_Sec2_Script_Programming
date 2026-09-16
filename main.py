"""จุดเริ่มโปรแกรมของเกม HOW_DO_YOU_FISH

รันด้วยคำสั่ง:  python main.py

เกมจะดึงชนิดปลาจาก WoRMS API ให้อัตโนมัติ ถ้าเชื่อมต่อไม่ได้จะสลับไปใช้
ฐานข้อมูลสำรองใน data/fish_species.json แล้วแจ้งให้ผู้เล่นทราบ
"""

import os
import sys

os.environ["PYTHONIOENCODING"] = "utf-8"

# บังคับ UTF-8 ทั้งขาเข้าและขาออก ป้องกันภาษาไทยเพี้ยนบน Windows Console
for _stream in (sys.stdin, sys.stdout):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")

from src.cli import FishingCLI  # noqa: E402

if __name__ == "__main__":
    FishingCLI().run()
