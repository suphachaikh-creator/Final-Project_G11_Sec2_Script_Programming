# Sprint 1 — Front-End App Dev (สัปดาห์ที่ 12)

โฟลเดอร์นี้คือซอร์สโค้ดทั้งหมดของ Sprint 1 — รันและทดสอบที่นี่
ส่วนรายงานประจำสปรินต์อยู่ที่ [`../notebook/Sprint1_Report.ipynb`](../notebook/Sprint1_Report.ipynb)

| ไฟล์ / โฟลเดอร์ | เนื้อหา |
|---|---|
| [`PLAN.md`](PLAN.md) | เอกสารวางแผน: ขอบเขต, Definition of Done, บทบาทในทีม |
| `main.py` | Entry point + บังคับ UTF-8 บน Windows Console |
| `src/` | โค้ดหลัก 4 โมดูล (app / ui / validators / mock_data) |
| `tests/` | ชุดทดสอบ pytest 36 เคส |
| `requirements.txt` · `.flake8` | dependency และมาตรฐาน PEP 8 |

## ขอบเขตของสปรินต์นี้

หน้าจอ CLI, ระบบเมนู และการตรวจสอบอินพุตเท่านั้น ข้อมูลทั้งหมดเก็บอยู่ใน memory
**ยังไม่เรียก API จริงและยังไม่บันทึกไฟล์จริง** — งานส่วนนั้นเป็นขอบเขตของ Sprint 2

## วิธีรัน

```bash
cd Sprint1/code
pip install -r requirements.txt
python main.py          # รันโปรแกรม
python -m pytest -q     # รันเทสต์ (36 เคส)
flake8 .                # ตรวจ PEP 8
```

## วิธีเปิดรายงาน

```bash
jupyter notebook Sprint1/notebook/Sprint1_Report.ipynb
```

เซลล์แรกสุดจะย้ายไปทำงานที่โฟลเดอร์ `code/` ให้อัตโนมัติ — **ต้องรันเซลล์นั้นก่อนเสมอ**
