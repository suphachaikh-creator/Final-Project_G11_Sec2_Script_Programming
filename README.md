# PixelPaw — Virtual Pet CLI

Final Term Project — CP352301 Script Programming (Group 11, Section 2)

แอปเลี้ยงสัตว์เสมือนจริงแบบ Command-Line พัฒนาแบบ Iterative ตามกำหนดการ 4 สปรินต์ของรายวิชา
**สถานะปัจจุบัน: Sprint 1 (Front-End App Dev) เสร็จแล้ว**

## โครงสร้างโปรเจกต์

```
Final-Project_G11_Sec2_Script_Programming/
├── .github/workflows/ci.yml       # CI: flake8 + pytest อัตโนมัติ
├── README.md
└── Sprint1/
    ├── code/                      # ซอร์สโค้ดทั้งหมด — รันและทดสอบที่นี่
    │   ├── PLAN.md                # เอกสารวางแผน + Definition of Done
    │   ├── README.md
    │   ├── main.py                # Entry point
    │   ├── requirements.txt
    │   ├── src/                   # app · ui · validators · mock_data
    │   └── tests/                 # pytest 36 เคส
    └── notebook/
        └── Sprint1_Report.ipynb   # รายงานประจำสปรินต์ (รันได้จริงทุกเซลล์)
```

## วิธีรัน

```bash
cd Sprint1/code
pip install -r requirements.txt
python main.py          # รันโปรแกรม
python -m pytest -q     # รันเทสต์ (36 เคส)
flake8 .                # ตรวจมาตรฐาน PEP 8
```

## สถาปัตยกรรม

แบ่งเลเยอร์ตามหลัก Separation of Concerns

| เลเยอร์ | ไฟล์ | หน้าที่ |
|---|---|---|
| Presentation | `src/ui.py` | แสดงผลทั้งหมด มีแต่ `print()` ไม่มีตรรกะ |
| Application | `src/app.py` | ลูปหลัก ระบบเมนู และการควบคุม Control Flow |
| Validation | `src/validators.py` | ตรวจสอบอินพุต ไม่มี `input()` / `print()` จึงทดสอบได้ตรง |
| Data (Mock) | `src/mock_data.py` | ข้อมูลสายพันธุ์จำลองใน memory |

## แผนรายสปรินต์ของรายวิชา

| สปรินต์ | สัปดาห์ | ขอบเขต | สถานะ |
|---|---|---|---|
| **Sprint 1** | 12 | Front-End App Dev: CLI, เมนู, Input Validation | ✅ เสร็จแล้ว |
| Sprint 2 | 13 | Back-End App Dev: Business Logic, Search/Filter/Sort, File I/O | 🔜 กำลังจะเริ่ม |
| Sprint 3 | 14 | Full-Stack: เชื่อม Front + Back, State, Edge Cases | ⏳ ยังไม่เริ่ม |
| Final Sprint | 15 | DevOps, CI/CD & AI Integration | ⏳ ยังไม่เริ่ม |

> **กติกาของ Sprint 1:** ห้ามเขียน business logic จริง ห้ามเรียก API จริง ห้ามบันทึกไฟล์จริง
> ข้อมูลทั้งหมดจึงเก็บอยู่ใน memory และใช้ข้อมูลจำลองแทนผลลัพธ์จาก API

## Continuous Integration

[`.github/workflows/ci.yml`](.github/workflows/ci.yml) รันอัตโนมัติทุก push และ pull request

1. ติดตั้ง dependency จาก `requirements.txt`
2. ตรวจมาตรฐานโค้ด PEP 8 ด้วย `flake8`
3. รันชุดทดสอบด้วย `pytest`

ชุดทดสอบทำงานแบบออฟไลน์ทั้งหมด ไม่ต้องตั้งค่า secret ใดๆ ใน GitHub

## ทีมงาน

| บทบาท | ผู้รับผิดชอบ |
|---|---|
| Project Manager / CI-CD Integrator | _รอระบุ_ |
| Automated Tester & QA | _รอระบุ_ |
| Core Developer | ศุภชัย คนเพียร |
