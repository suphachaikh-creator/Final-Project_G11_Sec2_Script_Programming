# PixelPaw — Virtual Pet CLI

Final Term Project — CP352301 Script Programming (Group 11, Section 2)

## โครงสร้างโปรเจกต์

แต่ละสปรินต์เป็นโฟลเดอร์ใหญ่ ภายในแยก **โค้ด** กับ **รายงาน (.ipynb)** ออกจากกัน

```
Final-Project_G11_Sec2_Script_Programming/
├── .github/workflows/ci.yml       # CI ตรวจทั้งสองสปรินต์แบบ matrix
├── .gitignore
├── README.md
├── Sprint1/                       # Front-End App Dev (สัปดาห์ 12)
│   ├── code/                      # โค้ดทั้งหมด — รันและทดสอบที่นี่
│   │   ├── PLAN.md                # เอกสารวางแผนของสปรินต์
│   │   ├── README.md
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   ├── src/
│   │   └── tests/
│   └── notebook/
│       └── Sprint1_Report.ipynb   # รายงานประจำสปรินต์
└── Sprint2/                       # Back-End App Dev (สัปดาห์ 13)
    ├── code/
    │   ├── README.md
    │   ├── main.py
    │   ├── requirements.txt
    │   ├── data/
    │   ├── src/
    │   ├── tests/
    │   └── tools/
    └── notebook/
        └── Sprint2_Report.ipynb
```

| โฟลเดอร์ | ขอบเขต | รันด้วย |
|---|---|---|
| [`Sprint1/code`](Sprint1/code) | **Front-End** — หน้าจอ CLI, ระบบเมนู, การตรวจสอบอินพุต (ข้อมูลจำลองใน memory) | `python main.py` |
| [`Sprint2/code`](Sprint2/code) | **Back-End** — ตรรกะการเลี้ยงแบบ OOP, เชื่อม Gemini API, บันทึก/โหลดไฟล์ JSON | `python main.py` |

โฟลเดอร์ `code/` ของแต่ละสปรินต์รันและทดสอบแยกกันได้ มี `requirements.txt` และ `.flake8` ของตัวเอง
ส่วนโน้ตบุ๊กใน `notebook/` ทุกเซลล์รันได้จริง — อ่านซอร์สจากไฟล์ใน `code/src/` และเรียก pytest กับ flake8
ชุดเดียวกับที่ CI ใช้ตรวจ จึงไม่มีทางที่เนื้อหารายงานจะหลุดจากโค้ด

## แผนรายสปรินต์ของรายวิชา

| สปรินต์ | สัปดาห์ | ขอบเขต | สถานะ |
|---|---|---|---|
| Sprint 1 | 12 | Front-End App Dev: CLI, เมนู, Input Validation | เสร็จแล้ว |
| Sprint 2 | 13 | Back-End App Dev: Business Logic, Search/Filter/Sort, File I/O | กำลังทำ |
| Sprint 3 | 14 | Full-Stack: เชื่อม Front + Back, State, Edge Cases | ยังไม่เริ่ม |
| Final Sprint | 15 | DevOps, CI/CD & AI Integration | ยังไม่เริ่ม |

> **กติกาสำคัญ:** Sprint 1 ห้ามเขียน business logic จริง ห้ามเรียก API จริง ห้ามบันทึกไฟล์จริง
> ดังนั้นงานส่วนดังกล่าวจึงอยู่ใน `Sprint2/code/` ทั้งหมด

## Continuous Integration

[`.github/workflows/ci.yml`](.github/workflows/ci.yml) รันอัตโนมัติทุก push และ pull request
โดยใช้ matrix ตรวจทั้งสองสปรินต์แบบขนาน (working directory คือ `<Sprint>/code`):

1. ติดตั้ง dependency จาก `requirements.txt` ของสปรินต์นั้น
2. ตรวจมาตรฐานโค้ด PEP 8 ด้วย `flake8`
3. รันชุดทดสอบด้วย `pytest`

ชุดทดสอบทั้งหมดทำงานแบบออฟไลน์ — ไม่เรียก API จริงและไม่แตะไฟล์เซฟจริง จึงไม่ต้องตั้งค่า
secret ใดๆ ใน GitHub

## คำสั่งที่ใช้บ่อย

```bash
cd Sprint1/code
pip install -r requirements.txt
python main.py          # รันโปรแกรม
python -m pytest -q     # รันเทสต์
flake8 .                # ตรวจ PEP 8
```
