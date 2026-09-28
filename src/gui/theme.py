"""ชุดสีและสไตล์ของหน้าจอ (Sprint 3 — Full-Stack)

ไฟล์นี้เก็บ **การตกแต่งอย่างเดียว** ไม่มีตรรกะของเกมเลย

ใช้ธีม `clam` ของ ttk เป็นฐาน เพราะเป็นธีมเดียวที่ปรับสีได้ทุกส่วนจริงๆ
ส่วน `vista` ที่เป็นค่าเริ่มต้นบน Windows จะไม่ยอมให้เปลี่ยนสีพื้นของปุ่ม
ทั้งหมดใช้ของที่มากับ Python ไม่ต้องติดตั้งไลบรารีเพิ่ม เครื่องไหนก็เปิดได้
"""

import tkinter.font as tkfont
from tkinter import ttk

# โทนทะเลลึก — พื้นเข้ม ตัวอักษรสว่าง อ่านสบายตาในห้องมืด
COLORS = {
    "bg": "#0B1D2A",          # พื้นหลังหลัก
    "sidebar": "#081520",     # แถบเมนูด้านซ้าย
    "surface": "#12293B",     # พื้นของการ์ด
    "surface_alt": "#18344A",  # พื้นของแถวสลับในตาราง
    "border": "#1E3D55",
    "accent": "#2EC4B6",      # เขียวน้ำทะเล — สีหลัก
    "accent_dark": "#23A295",
    "gold": "#FFB703",        # ทอง — เงินและรางวัล
    "text": "#E8F1F8",
    "muted": "#8FA9BD",       # ข้อความรอง
    "success": "#6BCB77",
    "danger": "#FF6B6B",
}

# ฟอนต์ไทยที่มากับ Windows ถ้าไม่มีจะถอยไปใช้ค่าเริ่มต้นของระบบเอง
FONT_FAMILY = "Leelawadee UI"
MONO_FAMILY = "Consolas"

PAD = 16
RADIUS = 10


def pick_family(root, preferred, fallback="TkDefaultFont"):
    """เลือกฟอนต์ที่มีอยู่จริงในเครื่อง ถ้าไม่มีให้ใช้ของระบบ"""
    available = set(tkfont.families(root))
    return preferred if preferred in available else fallback


def apply_theme(root):
    """ตั้งค่าสีและฟอนต์ให้วิดเจ็ตทุกตัว คืน dict ของฟอนต์ที่เลือกได้"""
    family = pick_family(root, FONT_FAMILY)
    mono = pick_family(root, MONO_FAMILY)

    fonts = {
        "title": (family, 22, "bold"),
        "heading": (family, 15, "bold"),
        "body": (family, 11),
        "small": (family, 10),
        "number": (family, 20, "bold"),
        "mono": (mono, 20, "bold"),
    }

    root.configure(bg=COLORS["bg"])
    style = ttk.Style(root)
    style.theme_use("clam")

    # ---------------------------------------------------------- พื้นและข้อความ
    style.configure(".", background=COLORS["bg"], foreground=COLORS["text"],
                    font=fonts["body"], borderwidth=0, focuscolor=COLORS["accent"])
    style.configure("TFrame", background=COLORS["bg"])
    style.configure("Card.TFrame", background=COLORS["surface"])
    style.configure("Sidebar.TFrame", background=COLORS["sidebar"])

    style.configure("TLabel", background=COLORS["bg"], foreground=COLORS["text"])
    style.configure("Card.TLabel", background=COLORS["surface"],
                    foreground=COLORS["text"])
    style.configure("Muted.TLabel", background=COLORS["surface"],
                    foreground=COLORS["muted"], font=fonts["small"])
    style.configure("Heading.TLabel", background=COLORS["surface"],
                    foreground=COLORS["text"], font=fonts["heading"])
    style.configure("Title.TLabel", background=COLORS["bg"],
                    foreground=COLORS["text"], font=fonts["title"])
    style.configure("Gold.TLabel", background=COLORS["surface"],
                    foreground=COLORS["gold"], font=fonts["number"])
    style.configure("Success.TLabel", background=COLORS["surface"],
                    foreground=COLORS["success"])
    style.configure("Danger.TLabel", background=COLORS["surface"],
                    foreground=COLORS["danger"])

    # ------------------------------------------------------------------- ปุ่ม
    style.configure("TButton", background=COLORS["surface_alt"],
                    foreground=COLORS["text"], padding=(14, 9),
                    font=fonts["body"], relief="flat")
    style.map("TButton",
              background=[("disabled", COLORS["surface"]),
                          ("pressed", COLORS["border"]),
                          ("active", COLORS["border"])],
              foreground=[("disabled", COLORS["muted"])])

    style.configure("Accent.TButton", background=COLORS["accent"],
                    foreground=COLORS["bg"], font=(family, 12, "bold"),
                    padding=(18, 11))
    style.map("Accent.TButton",
              background=[("disabled", COLORS["surface_alt"]),
                          ("active", COLORS["accent_dark"])],
              foreground=[("disabled", COLORS["muted"])])

    style.configure("Gold.TButton", background=COLORS["gold"],
                    foreground="#2A1A00", font=(family, 11, "bold"),
                    padding=(14, 9))
    style.map("Gold.TButton",
              background=[("disabled", COLORS["surface_alt"]),
                          ("active", "#E0A000")],
              foreground=[("disabled", COLORS["muted"])])

    # ปุ่มเมนูด้านซ้าย — จัดชิดซ้ายให้ดูเป็นรายการ ไม่ใช่ปุ่มลอย
    style.configure("Nav.TButton", background=COLORS["sidebar"],
                    foreground=COLORS["muted"], anchor="w",
                    padding=(16, 12), font=fonts["body"])
    style.map("Nav.TButton",
              background=[("active", COLORS["surface"])],
              foreground=[("active", COLORS["text"])])

    style.configure("NavActive.TButton", background=COLORS["surface"],
                    foreground=COLORS["accent"], anchor="w",
                    padding=(16, 12), font=(family, 11, "bold"))
    style.map("NavActive.TButton", background=[("active", COLORS["surface"])])

    # ------------------------------------------------------------ ช่องกรอกและตาราง
    style.configure("TEntry", fieldbackground=COLORS["surface_alt"],
                    foreground=COLORS["text"], insertcolor=COLORS["accent"],
                    bordercolor=COLORS["border"], padding=8)
    style.configure("TCombobox", fieldbackground=COLORS["surface_alt"],
                    background=COLORS["surface_alt"], foreground=COLORS["text"],
                    arrowcolor=COLORS["accent"], padding=6)
    style.map("TCombobox",
              fieldbackground=[("readonly", COLORS["surface_alt"])],
              selectbackground=[("readonly", COLORS["surface_alt"])],
              selectforeground=[("readonly", COLORS["text"])])

    style.configure("Treeview", background=COLORS["surface"],
                    fieldbackground=COLORS["surface"], foreground=COLORS["text"],
                    rowheight=30, borderwidth=0, font=fonts["body"])
    style.configure("Treeview.Heading", background=COLORS["surface_alt"],
                    foreground=COLORS["muted"], relief="flat",
                    padding=(10, 8), font=(family, 10, "bold"))
    style.map("Treeview.Heading",
              background=[("active", COLORS["border"])],
              foreground=[("active", COLORS["accent"])])
    style.map("Treeview",
              background=[("selected", COLORS["accent"])],
              foreground=[("selected", COLORS["bg"])])

    style.configure("TRadiobutton", background=COLORS["surface"],
                    foreground=COLORS["text"], font=fonts["body"])
    style.map("TRadiobutton",
              background=[("active", COLORS["surface"])],
              foreground=[("active", COLORS["accent"])])

    style.configure("TSeparator", background=COLORS["border"])
    style.configure("TScrollbar", background=COLORS["surface_alt"],
                    troughcolor=COLORS["bg"], arrowcolor=COLORS["muted"])

    return fonts


def time_color(ratio):
    """สีของแถบเวลา — เหลือมากเป็นเขียว เหลือน้อยเป็นทอง แล้วเป็นแดง

    ช่วยให้ผู้เล่นรู้ว่าใกล้หมดเวลาโดยไม่ต้องอ่านตัวเลข
    """
    if ratio > 0.5:
        return COLORS["accent"]
    if ratio > 0.25:
        return COLORS["gold"]
    return COLORS["danger"]
