# Sprint 2 — Back-End App Dev (สัปดาห์ที่ 13)

โฟลเดอร์นี้รวมงานที่ **เกินขอบเขตของ Sprint 1** ซึ่งย้ายออกมาจาก `Sprint1/` ได้แก่
การเรียก API จริง การอ่าน/เขียนไฟล์ JSON จริง และตรรกะการเลี้ยงน้องแมวจริง

โฟลเดอร์นี้คือซอร์สโค้ดทั้งหมดของ Sprint 2 — รันและทดสอบที่นี่
ส่วนรายงานประจำสปรินต์อยู่ที่ [`../notebook/Sprint2_Report.ipynb`](../notebook/Sprint2_Report.ipynb)

## ขอบเขตของสปรินต์นี้

| งาน | ไฟล์ | สถานะ |
|---|---|---|
| ตรรกะการเลี้ยง (feed / play / rest) แบบ OOP | `src/pet.py` | ทำแล้ว |
| เชื่อม Gemini API ดึงข้อมูลสายพันธุ์แมว | `src/api_client.py` | ทำแล้ว |
| บันทึก/โหลดสถานะเป็นไฟล์ JSON | `src/app_functions.py` | ทำแล้ว |
| ลูปการเลี้ยงที่เชื่อมตรรกะจริง | `src/game.py` | ทำแล้ว |
| เมนูหลักเชื่อม API + เซฟไฟล์ | `src/app.py` | ทำแล้ว |
| Search / Filter / Sort รายการสายพันธุ์ | — | ยังไม่ทำ |
| Time decay (ค่าสถานะลดตามเวลาจริง) | — | ยังไม่ทำ |

## โครงสร้างไฟล์

```
Sprint2/
├── code/                             # โฟลเดอร์นี้ — ซอร์สโค้ดทั้งหมด
│   ├── README.md                     # เอกสารฉบับนี้
│   ├── main.py                       # Entry point — python main.py
│   ├── requirements.txt              # google-genai + pytest + flake8
│   ├── .env.example                  # ตัวอย่างการตั้งค่า GEMINI_API_KEY
│   ├── data/pet_state.json           # ไฟล์เซฟสถานะน้องแมว
│   ├── src/
│   │   ├── app.py                    # เมนูหลัก
│   │   ├── game.py                   # ลูปการเลี้ยง
│   │   ├── pet.py                    # คลาส Pet (ตรรกะ + serialization)
│   │   ├── api_client.py             # เรียก Gemini API
│   │   ├── app_functions.py          # save_game / load_game / fetch_new_pets
│   │   └── key.py                    # อ่าน GEMINI_API_KEY จาก environment
│   ├── tests/                        # เทสต์ออฟไลน์ทั้งหมด ไม่ต้องใช้ API Key
│   └── tools/check_api_connection.py # สคริปต์ตรวจการเชื่อมต่อ API ด้วยมือ
└── notebook/
    └── Sprint2_Report.ipynb
```

## วิธีรัน

```bash
cd Sprint2/code
pip install -r requirements.txt
python main.py          # รันเกม
python -m pytest -q     # รันเทสต์ (23 เคส)
flake8 .                # ตรวจ PEP 8
```

## การตั้งค่า API Key

`src/key.py` อ่านค่าจาก environment variable ไม่เก็บคีย์ไว้ในโค้ด

```powershell
$env:GEMINI_API_KEY = "คีย์ของคุณ"
python main.py
```

## หมายเหตุเรื่องการทดสอบ

ชุดเทสต์ใน `tests/` **ไม่เรียก API จริงและไม่แตะไฟล์เซฟจริง** (ใช้ `tmp_path` + `monkeypatch`)
จึงรันบน GitHub Actions ได้โดยไม่ต้องใส่ API Key
ส่วนการตรวจการเชื่อมต่อจริงอยู่ใน `tools/check_api_connection.py` ซึ่งตั้งใจไม่ตั้งชื่อ `test_*`
เพื่อไม่ให้ CI เรียกใช้
