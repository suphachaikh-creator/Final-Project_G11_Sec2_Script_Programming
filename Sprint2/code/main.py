"""Entry point ของ Sprint 2 - รันด้วยคำสั่ง: python main.py"""

import os
import sys

os.environ["PYTHONIOENCODING"] = "utf-8"

# บังคับใช้ UTF-8 ทั้งขาเข้าและขาออก ป้องกันภาษาไทยเพี้ยนบน Windows Console
for _stream in (sys.stdin, sys.stdout):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")

from src.app import main_menu  # noqa: E402

if __name__ == "__main__":
    main_menu()
