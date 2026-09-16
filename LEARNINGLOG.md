# 📓 Learning Log & Responsible AI Prompt Record (HOW_DO_YOU_FISH)

**Project Title:** HOW_DO_YOU_FISH — เกมจำลองการตกปลา · Final Project in Script Programming
**รายวิชา:** CP352301 Script Programming · Group 7 Section 2

**Team Members & Roles:**
- 🧭 **ศุภชัย คนเพียร 663380576-0** — Planner / PM · CI-CD Integrator
- 🧪 **ยศพล ถิรพงศชาติ 663380568-9** — Debugger / QA
- 💻 **ภาวัต วงศ์มาลาสิทธิ์ 663380636-8** — Coder (ชั้นตรรกะ)
- 💻 **ธนภัทร สมบูรณ์ 663380347-5** — Coder (ชั้นเชื่อมต่อและข้อมูล)

> บทบาท Planner และ Debugger/QA **หมุนเวียนทุกสปรินต์** ตารางว่าใครรับบทไหน
> อยู่ใน [PLAN.md](./PLAN.md) หัวข้อ 2

---

## 1. Context & Educational Rationale

เอกสารฉบับนี้บันทึกคำถามที่ทีมใช้ร่วมกับ AI ระหว่างพัฒนา พร้อมสิ่งที่ได้เรียนรู้จริง
จุดสำคัญคือทีมไม่ได้รับคำตอบของ AI มาใช้ทันที แต่**ทดสอบก่อนทุกครั้ง** และหลายครั้ง
การทดสอบนั้นเองที่พาไปเจอปัญหาที่ไม่มีใครถาม เช่น การค้นพบว่า `.isdigit()` ไม่ปลอดภัย
และการค้นพบว่าโค้ดเรียก API ไม่สำเร็จมาตลอดโดยไม่มีใครรู้

โครงการนี้ยึดหลัก **Separation of Concerns** อย่างเคร่งครัด แบ่งเป็น
Presentation · Application · Validation · Domain · Integration · Data Access
และออกแบบให้ **เครือข่าย เวลา และการสุ่ม** ถูกฉีดเข้ามาจากภายนอกได้ตั้งแต่ต้น
เพื่อให้ทดสอบได้โดยไม่ต้องพึ่งอินเทอร์เน็ตและไม่ต้องรอเวลาจริง

---

## 2. Records of AI Prompts & Responses

### 🔹 Prompt 1: แยกโค้ดก้อนเดียว 415 บรรทัดออกเป็นชั้น

- **Student Prompt:**
  ```text
  โค้ดเกมตกปลาตอนนี้รวมทุกอย่างไว้ในคลาสเดียวชื่อ FishingGame ยาว 415 บรรทัด
  มีทั้งการ print หน้าจอ รับ input คำนวณราคา และอ่านเขียนไฟล์ปนกันหมด
  ช่วยออกแบบใหม่ให้แยกชั้นตามหลัก Separation of Concerns และเขียน unit test ได้
  ```
- **AI Response Summary:**
  แนะนำให้แยกเป็น 6 ชั้น โดยกติกาคือ **ชั้นล่างต้องไม่รู้จักชั้นบน** — `ui.py`
  มีแต่ `print()` ไม่มีการตัดสินใจ · `validators.py` ไม่มีทั้ง `input()` และ `print()`
  · `game_state.py` กับ `fish.py` เป็นตรรกะบริสุทธิ์ที่ไม่รู้ว่ามีหน้าจอหรือ API อยู่
- **Live Verification Code:**
  ```python
  from src.game_state import GameState
  from src.fish import Fish, FRESHWATER

  state = GameState(money=100)
  state.add_fish(Fish("Carp", FRESHWATER, 2.0, 40))
  print(state.summary())
  ```
- **Verified Result:**
  ```text
  {'count': 1, 'total_price': 40, 'average_weight': 2.0, 'heaviest': Fish('Carp', 2.0 kg, $40)}
  ```

---

### 🔹 Prompt 2: ตรวจอินพุตให้โปรแกรมพังไม่ได้

- **Student Prompt:**
  ```text
  เขียนฟังก์ชันตรวจอินพุตสำหรับเมนู CLI ที่ต้องรับมือกับค่าว่าง ตัวอักษร
  ค่าติดลบ ทศนิยม และค่านอกช่วง โดยห้ามมี input() หรือ print() อยู่ในฟังก์ชัน
  ```
- **AI Response Summary:**
  ให้ฟังก์ชันรับค่าเข้าแล้วคืนค่าออกหรือโยน `ValueError` พร้อมข้อความที่บอกวิธีแก้
  ไม่ใช่แค่บอกว่าผิด และให้ `.strip().lower()` ก่อนเทียบเสมอ เพื่อให้คำสั่งอย่าง
  `" Back "` กับ `"b"` ทำงานเหมือนกัน แนะนำให้เช็กด้วย `.isdigit()` ก่อนเรียก `int()`
- **Live Verification Code:**
  ```python
  from src.validators import validate_menu_choice

  for raw in ("3", "   ", "abc", "-1", "2.5", "9"):
      try:
          print(raw, "->", validate_menu_choice(raw, 1, 4))
      except ValueError as error:
          print(raw, "-> ปฏิเสธ:", error)
  ```
- **Verified Result:**
  ```text
  3 -> 3
  (ว่าง) -> ปฏิเสธ: กรุณาพิมพ์ตัวเลือก ห้ามเว้นว่าง
  abc -> ปฏิเสธ: กรุณาเลือกเป็นตัวเลข 1 ถึง 4 เท่านั้น
  -1 -> ปฏิเสธ · 2.5 -> ปฏิเสธ · 9 -> ปฏิเสธ (นอกช่วง)
  ```

---

### 🔹 Prompt 3: บั๊กที่เจอเองจากการเขียนเทสต์ — `.isdigit()` ไม่ปลอดภัย

- **Student Prompt:**
  ```text
  เขียนเทสต์ให้เลขไทย "๑" ถูกปฏิเสธ แต่เทสต์ล้มเพราะฟังก์ชันดันยอมรับ
  ช่วยอธิบายว่า .isdigit() ต่างจาก .isdecimal() อย่างไร และแบบไหนปลอดภัยกว่า
  ```
- **AI Response Summary:**
  `.isdigit()` คืน `True` ให้ตัวยกอย่าง `"²"` และ `"³"` ด้วย แต่ `int()` แปลงไม่ได้
  จึงเป็นช่องที่ทำให้โปรแกรมพังทั้งที่ผ่านด่านตรวจไปแล้ว ส่วน `.isdecimal()`
  คืน `False` ให้ตัวยก แต่ยังคืน `True` ให้เลขไทยซึ่ง `int()` แปลงได้จริง
- **Live Verification Code:**
  ```python
  print("²".isdigit(), "²".isdecimal())
  print("๑".isdigit(), "๑".isdecimal(), int("๑"))
  try:
      int("²")
  except ValueError as error:
      print("int('²') ->", error)
  ```
- **Verified Result:**
  ```text
  True False
  True True 1
  int('²') -> invalid literal for int() with base 10: '²'
  ```
- **บทเรียน:** เทสต์ที่เขียนไว้เพื่อยืนยันเรื่องหนึ่ง กลับพาไปเจอบั๊กคนละเรื่องที่ร้ายแรงกว่า

---

### 🔹 Prompt 4: ทำมินิเกมจับเวลาให้ทดสอบได้โดยไม่ต้องรอจริง

- **Student Prompt:**
  ```text
  มินิเกม QTE ต้องจับเวลาถอยหลัง ถ้าเขียนแบบเรียก time.time() ตรงๆ
  เวลาจะเขียนเทสต์เรื่องหมดเวลาต้อง sleep รอจริงหลายวินาที ทำให้ CI ช้า
  มีวิธีออกแบบให้ทดสอบได้โดยไม่ต้องรอไหม
  ```
- **AI Response Summary:**
  ให้ **ฉีดนาฬิกาเข้ามาทาง constructor** (`clock=None` แล้ว default เป็น
  `time.monotonic`) ตอนเล่นจริงใช้นาฬิกาจริง ตอนทดสอบใส่นาฬิกาจำลองที่เดินเองได้
  หลักเดียวกันใช้กับ `rng` ได้ด้วย ทำให้ผลสุ่มกำหนดค่าตายตัวได้
- **Live Verification Code:**
  ```python
  from src.minigame import QTEMinigame

  now = [0.0]
  game = QTEMinigame(rod_level=1, clock=lambda: now[0])
  game.start()
  print("เริ่มต้น", game.time_left())
  now[0] = 99.0
  print("หลังเดินเวลา", game.time_left(), "หมดเวลา:", game.is_timed_out())
  ```
- **Verified Result:**
  ```text
  เริ่มต้น 6.5
  หลังเดินเวลา 0.0 หมดเวลา: True
  ```
- **บทเรียน:** การออกแบบเพื่อทดสอบตั้งแต่ต้น ได้ผลพลอยได้ใน Sprint ถัดไปด้วย

---

### 🔹 Prompt 5: เลือก endpoint ของ WoRMS ให้ถูกตัว

- **Student Prompt:**
  ```text
  ใช้ WoRMS API ดึงชนิดปลา ลองค้นคำว่า fish และ shark ด้วย AphiaRecordsByName
  แล้วได้ผลแปลกๆ ที่ไม่ใช่ปลาเลย ช่วยตรวจว่าใช้ endpoint ถูกหรือเปล่า
  ```
- **AI Response Summary:**
  `AphiaRecordsByName` ค้นจาก **ชื่อวิทยาศาสตร์** จึงไปตรงกับสกุลที่สะกดคล้ายกัน
  เช่น *Fisherana* ซึ่งเป็นหนอนทะเล ไม่ใช่ปลา ถ้าต้องการค้นจากคำสามัญอย่าง `carp`
  ต้องใช้ `AphiaRecordsByVernacular` แทน และควรกรองด้วย `class` กับ `status`
- **Live Verification Code:**
  ```python
  from src.worms_api import WormsAPI
  print(len(WormsAPI().fetch_fish_records()), "ชนิด")
  ```
- **Verified Result:**
  ```text
  AphiaRecordsByName  : ได้ปลา 0 จาก 115 รายการ  (ไม่เหมาะ)
  AphiaRecordsByVernacular : 650 ชนิด            (เลือกใช้ตัวนี้)
  ```
- **บทเรียน:** ต้องยิง API จริงดูผลก่อนตัดสินใจ อย่าเชื่อชื่อ endpoint

---

### 🔹 Prompt 6: รวมสอง Public API ให้ชื่อปลาอ่านรู้เรื่อง

- **Student Prompt:**
  ```text
  WoRMS บอกแหล่งน้ำได้แต่คืนแค่ชื่อวิทยาศาสตร์อย่าง Salmo salar ผู้เล่นอ่านไม่รู้เรื่อง
  ใช้ทั้ง WoRMS และ Open Fisheries พร้อมกันได้ไหม
  ```
- **AI Response Summary:**
  ทำได้โดยจับคู่สองแหล่งด้วย **ชื่อวิทยาศาสตร์** ให้ WoRMS เป็นข้อมูลหลัก
  (บอกแหล่งน้ำ) และ Open Fisheries เป็นข้อมูลเสริม (ชื่อสามัญ) จุดสำคัญคือต้องแยก
  **ระดับความสำคัญ** — ข้อมูลเสริมล้มเหลวได้โดยเกมยังเล่นต่อได้
- **Live Verification Code:**
  ```python
  from src.fish_api import FishAPI
  from src.fish import FRESHWATER, MARINE, BRACKISH

  api = FishAPI()
  for location in (FRESHWATER, MARINE, BRACKISH):
      species = api.fetch_species(location)
      named = sum(1 for s in species if s["name"] != s["scientific_name"])
      print(f"{location:<12}{len(species):>4} ชนิด | มีชื่อสามัญ {named}")
  ```
- **Verified Result:**
  ```text
  freshwater   111 ชนิด | มีชื่อสามัญ  51
  marine       316 ชนิด | มีชื่อสามัญ 217
  brackish     126 ชนิด | มีชื่อสามัญ  88
  Open Fisheries: 11,562 รายการ -> จับคู่ได้ 8,672 คู่
  ```

---

### 🔹 Prompt 7: บั๊กที่ทำให้เกมไม่เคยเรียก API สำเร็จเลย

- **Student Prompt:**
  ```text
  เกมใช้ข้อมูลสำรองในเครื่องตลอดเวลา ทั้งที่อินเทอร์เน็ตใช้งานได้ปกติ
  แต่ไม่มีข้อความ error ขึ้นมาเลยสักครั้ง ช่วยหาสาเหตุ
  ```
- **AI Response Summary:**
  ต้นเหตุคือ `except Exception: pass` ที่ครอบการเรียก API ไว้ ทำให้ความผิดพลาด
  ทุกชนิดถูกกลืนหายไปเงียบๆ แนะนำให้ดัก error เป็นชนิดที่เจาะจง
  (`ConnectionError` · `Timeout` · `HTTPError` · `JSONDecodeError`) และ
  **เก็บข้อความไว้เสมอ** พร้อมตั้งธงบอกสถานะให้หน้าจอแสดงได้
- **Live Verification Code:**
  ```python
  api = FishAPI()
  api.fetch_species("freshwater")
  print("using_fallback:", api.using_fallback, "| last_error:", api.last_error)
  ```
- **Verified Result:**
  ```text
  ก่อนแก้ : using_fallback ตลอดเวลา แต่ last_error เป็น None (ไม่มีใครรู้ว่าพัง)
  หลังแก้ : using_fallback: False | last_error: None  (เรียก API สำเร็จจริง)
  ```
- **บทเรียน:** `except Exception: pass` อันตรายกว่าที่คิด เพราะซ่อนปัญหาไว้นาน

---

### 🔹 Prompt 8: เรียงลำดับแล้วเผลอทำลายข้อมูลจริง

- **Student Prompt:**
  ```text
  ฟังก์ชันเรียงลำดับปลาในกระเป๋าควรใช้ list.sort() หรือ sorted() ดี
  เพราะผู้เล่นแค่อยากดูผลเรียง ไม่ได้อยากให้ลำดับในกระเป๋าเปลี่ยนถาวร
  ```
- **AI Response Summary:**
  `list.sort()` แก้ลิสต์ต้นฉบับทันที ถ้าใช้กับ `self.inventory` ลำดับจริงจะเปลี่ยน
  และไปกระทบไฟล์เซฟตอนบันทึกครั้งถัดไป ควรใช้ `sorted()` ที่คืนลิสต์ใหม่แทน
  แล้วเขียนเทสต์ล็อกไว้ไม่ให้ใครเผลอเปลี่ยนกลับ
- **Live Verification Code:**
  ```python
  before = list(state.inventory)
  state.sort_inventory("weight")
  assert state.inventory == before, "การเรียงต้องไม่เปลี่ยนลำดับจริง"
  print("ลำดับในกระเป๋าไม่ถูกแตะต้อง")
  ```
- **Verified Result:**
  ```text
  ลำดับในกระเป๋าไม่ถูกแตะต้อง
  (เทสต์ test_sort_does_not_mutate_inventory ล็อกไว้แล้ว)
  ```

---

### 🔹 Prompt 9: ไฟล์เซฟเสียหายต้องไม่ทำให้เปิดเกมไม่ได้

- **Student Prompt:**
  ```text
  ถ้าไฟล์ save_game.json หาย เสียหาย หรือถูกแก้มือจนโครงสร้างผิด
  เกมต้องไม่ crash ควรดักอย่างไรและทดสอบอย่างไรโดยไม่แตะไฟล์จริงของผู้เล่น
  ```
- **AI Response Summary:**
  ให้ `load()` คืน `None` แทนการโยน exception และดัก `json.JSONDecodeError` ·
  `ValueError` · `OSError` · `TypeError` ส่วนการทดสอบให้ใช้ `tmp_path` ของ pytest
  ซึ่งสร้างโฟลเดอร์ชั่วคราวให้อัตโนมัติ และแนะนำ `ensure_ascii=False`
  เพื่อให้ชื่อปลาภาษาไทยอ่านออกในไฟล์
- **Live Verification Code:**
  ```python
  def test_broken_file(tmp_path):
      path = tmp_path / "save.json"
      path.write_text("{ ไม่ใช่ JSON", encoding="utf-8")
      saver = SaveManager(str(path))
      assert saver.load() is None
      assert "เสียหาย" in saver.last_error
  ```
- **Verified Result:**
  ```text
  10 passed — ครอบคลุมไฟล์หาย ไฟล์เสีย ไฟล์ไม่ใช่ object ฟิลด์ขาด และ round-trip
  ```

---

### 🔹 Prompt 10: ไฟล์ข้อมูลสำรองมีชื่อสามัญแค่ 20%

- **Student Prompt:**
  ```text
  สคริปต์สร้างไฟล์ข้อมูลสำรองดึงมา 90 ชนิด แต่มีชื่อสามัญแค่ 18 ชนิด
  ทั้งที่ตอนดึงสดมีถึง 64% ช่วยหาสาเหตุ
  ```
- **AI Response Summary:**
  สคริปต์เรียงตามตัวอักษรก่อนตัดด้วย `--limit` ชนิดที่ไม่มีชื่อสามัญจึงถูกเลือก
  ขึ้นมาก่อนโดยบังเอิญ แก้โดยเปลี่ยน key ของการเรียงให้เอาชนิดที่**มีชื่อสามัญ
  ขึ้นก่อน** แล้วค่อยเรียงตามตัวอักษรเป็นลำดับรอง
- **Live Verification Code:**
  ```python
  matched.sort(key=lambda item: (item["name"] == item["scientific_name"],
                                 item["name"].lower()))
  ```
- **Verified Result:**
  ```text
  ก่อนแก้ : รวม 90 รายการ  มีชื่อสามัญ 18 รายการ (20%)
  หลังแก้ : รวม 90 รายการ  มีชื่อสามัญ 90 รายการ (100%)
  ```

---

### 🔹 Prompt 11: ตั้ง CI ให้รันอัตโนมัติทุก push

- **Student Prompt:**
  ```text
  ตั้ง GitHub Actions ให้รัน flake8 และ pytest ทุกครั้งที่ push และตอนเปิด
  Pull Request โดยใช้ Python 3.11 และแคช pip
  ```
- **AI Response Summary:**
  ใช้ `actions/checkout@v4` กับ `actions/setup-python@v5` ที่มี `cache: pip`
  และผูก `cache-dependency-path` กับ `requirements.txt` แยกขั้นตอน lint
  กับ test ออกจากกันเพื่อให้เห็นชัดว่าพังเพราะอะไร
- **Test Command:**
  ```text
  python -m pytest -q
  flake8 .
  ```
- **Verified Result:**
  ```text
  135 passed · flake8 0 issues
  CI บน GitHub Actions: completed / success
  ```

---

## 3. Key Learning Outcomes

- **การแบ่งชั้นทำให้เขียนเทสต์ได้โดยไม่ต้อง mock อะไรเลย** — เพราะ `validators.py`
  ไม่มี `input()` และ `game_state.py` ไม่แตะไฟล์ จึงยิงเทสต์ตรงเข้าไปได้ทันที
- **การฉีดของเข้ามาจากภายนอกคือหัวใจของการทดสอบ** — `http` · `clock` · `rng`
  ทำให้เทสต์ทั้งชุดรันออฟไลน์ ไม่รอเวลาจริง และผลลัพธ์แน่นอนทุกครั้ง
- **`.isdigit()` ไม่ปลอดภัยสำหรับการแปลงเป็นตัวเลข** ต้องใช้ `.isdecimal()`
- **`except Exception: pass` ซ่อนปัญหาได้นานมาก** ต้องดักให้เจาะจงและเก็บ error ไว้เสมอ
- **`sorted()` กับ `.sort()` ต่างกันตรงที่ตัวหลังทำลายข้อมูลต้นฉบับ**
- **ต้องทดสอบ API จริงก่อนเชื่อเอกสาร** — endpoint ที่ชื่อดูเหมาะอาจให้ผล 0 รายการ
- **ของเสริมต้องล้มเหลวได้** — Open Fisheries ล่มแล้วเกมยังเล่นได้ เป็นหลักที่ใช้ซ้ำได้
- **`tmp_path` ของ pytest** ทำให้ทดสอบการอ่านเขียนไฟล์โดยไม่แตะข้อมูลจริงใน `data/`

---

## 4. Reflection / Retrospective

### Wow!

- แยกโค้ดก้อนเดียว 415 บรรทัดออกเป็น 6 ชั้นได้สำเร็จ และเขียนเทสต์ครอบได้ **135 เคส**
  รันเสร็จในเสี้ยววินาทีเพราะไม่มีเคสไหนรอเวลาจริงหรือรอเครือข่าย
- ใช้ Public API **สองตัวพร้อมกัน** โดยจับคู่ด้วยชื่อวิทยาศาสตร์ ทำให้ได้ทั้งแหล่งน้ำ
  ที่ถูกต้องและชื่อที่ผู้เล่นอ่านรู้เรื่อง
- เกม **เล่นได้แม้ไม่มีอินเทอร์เน็ต** เพราะมีไฟล์ข้อมูลสำรองที่มีชื่อสามัญครบ 100%
- เทสต์พาไปเจอบั๊กที่ไม่มีใครตั้งใจหา ทั้งเรื่องตัวยกและเรื่องการเรียงลำดับ

### Whoops!

- **เชื่อ `.isdigit()` มากเกินไป** ทำให้มีช่องที่โปรแกรมพังได้จากตัวยก แก้เป็น `.isdecimal()`
- **`except Exception: pass` ทำให้ API พังโดยไม่มีใครรู้** เป็นเวลานาน
  บทเรียนคือความเงียบไม่ได้แปลว่าทุกอย่างเรียบร้อย
- **เลือก endpoint ผิดตัวจนได้ปลา 0 จาก 115 รายการ** เพราะดูแค่ชื่อ endpoint
  ไม่ได้ยิงดูผลจริงก่อน
- **ลืมดัก `EOFError`** ทำให้โปรแกรมพังเมื่อรันแบบ pipe แก้โดยดักใน `FishingCLI.ask()`
  แล้วถือว่าผู้ใช้สั่งออกจากโปรแกรม
- **เกือบเผลอเรียงลำดับทับข้อมูลจริงในกระเป๋า** จับได้ตอนเขียนเทสต์

---

## 5. Evidence of Work

| ส่วน | ไฟล์ |
|---|---|
| จุดเริ่มโปรแกรม | [main.py](./main.py) |
| Presentation | [src/ui.py](./src/ui.py) |
| Application | [src/cli.py](./src/cli.py) · [src/minigame.py](./src/minigame.py) |
| Validation | [src/validators.py](./src/validators.py) |
| Domain | [src/game_state.py](./src/game_state.py) · [src/fish.py](./src/fish.py) |
| Integration | [src/worms_api.py](./src/worms_api.py) · [src/openfisheries_api.py](./src/openfisheries_api.py) · [src/fish_api.py](./src/fish_api.py) |
| Data Access | [src/save_manager.py](./src/save_manager.py) |
| เครื่องมือ | [tools/seed_fish_data.py](./tools/seed_fish_data.py) |
| ชุดทดสอบ 135 เคส | [tests/](./tests/) |
| CI Pipeline | [.github/workflows/ci.yml](./.github/workflows/ci.yml) |
| แผนงาน | [PLAN.md](./PLAN.md) |
| บันทึกเวอร์ชัน | [CHANGELOG.md](./CHANGELOG.md) |
| รายงานสปรินต์ | [reports/sprint1_report.md](./reports/sprint1_report.md) · [reports/sprint2_report.md](./reports/sprint2_report.md) |
