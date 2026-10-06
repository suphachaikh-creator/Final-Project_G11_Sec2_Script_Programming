# แนวทางการร่วมพัฒนา

เอกสารนี้สรุปกติกาที่ทีมใช้จริงตลอดโปรเจกต์ **HOW_DO_YOU_FISH**
ใครเข้ามาทำต่อควรอ่านก่อนเขียนโค้ดบรรทัดแรก

---

## 1. เตรียมเครื่อง

```bash
git clone https://github.com/suphachaikh-creator/Final-Project_G11_Sec2_Script_Programming.git
cd Final-Project_G11_Sec2_Script_Programming
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

รันเกม

```bash
python main.py                  # โหมด Desktop GUI
python main.py --cli            # โหมด Terminal
```

---

## 2. กฎการแบ่งชั้น — ข้อสำคัญที่สุด

โปรเจกต์นี้แยกชั้นอย่างเคร่งครัด **ก่อนเขียนโค้ดใหม่ ให้ถามก่อนว่ามันควรอยู่ชั้นไหน**

| ชั้น | ไฟล์ | ห้ามมีอะไร |
|---|---|---|
| Presentation | `ui.py` · `gui/app.py` · `gui/pages/` | กฎของเกม การคำนวณ การตัดสินใจ |
| Application | `cli.py` · `gui/presenter.py` · `gui/species_loader.py` | `print()` · `tkinter` (ยกเว้น `cli.py` ที่เป็นโหมด Terminal) |
| Validation | `validators.py` | `input()` · `print()` |
| Domain | `fish.py` · `game_state.py` · `minigame.py` · `difficulty.py` · `ai_fishing.py` | ไฟล์ หน้าจอ · เครือข่ายมีได้เฉพาะ Gemini ใน `ai_fishing.py` และต้องมีโหมดสำรอง |
| Integration | `worms_api.py` · `openfisheries_api.py` · `fish_api.py` · `update_checker.py` | กฎของเกม |
| Data Access | `save_manager.py` · `catch_log.py` | กฎของเกม หน้าจอ |

**ตัวอย่างที่ผิด** — เขียน `if state.money < cost:` ไว้ใน `gui/pages/shop.py`
**ตัวอย่างที่ถูก** — ถาม `presenter.items()` ว่าปุ่มควรกดได้ไหม แล้ว `shop.py` แค่ตั้งค่า `state="disabled"`

---

## 3. กฎการเขียนเทสต์

### 3.1 ห้ามยิงเครือข่ายจริง

ทุกคลาสที่เรียก API รับ `http` เข้ามาทาง constructor เทสต์ให้ใส่ตัวปลอมแทน

```python
api = WormsAPI(http=FakeHttp(FakeResponse([record])))
```

### 3.2 ห้ามรอเวลาจริง

`QTEMinigame` รับ `clock` เข้ามาได้ อย่าใช้ `time.sleep()` ในเทสต์เด็ดขาด

```python
clock = TkClock(1000)
presenter = FishingPresenter(state, api, clock=clock)
clock.tick()            # เดินเวลาทีละวินาทีโดยไม่ต้องรอจริง
```

### 3.3 ห้ามสร้าง `tk.Tk()` ในเทสต์

เครื่องที่รัน CI ไม่มีจอ ถ้าเปิดหน้าต่างจริงจะพังทันที
ตรรกะของหน้าจออยู่ใน `src/gui/presenter.py` ซึ่งไม่ import `tkinter` เลย — ให้เทสต์ยิงที่นั่น

### 3.4 ห้ามแตะไฟล์เซฟจริง

ใช้ `tmp_path` ของ pytest เสมอ

```python
def test_save(tmp_path):
    saver = SaveManager(str(tmp_path / "save.json"))
```

### 3.5 ห้ามยิง Gemini จริงในเทสต์

แทน `requests.post` ด้วยตัวปลอมผ่าน `monkeypatch` และลบ `GEMINI_API_KEY` ของเครื่องออกก่อนทุกเทสต์
ตัวอย่างอยู่ใน `tests/test_ai_fishing.py`

```python
monkeypatch.delenv("GEMINI_API_KEY", raising=False)
monkeypatch.setattr(ai_fishing.requests, "post", FakePost(FakeResponse(status_code=503)))
```

**ห้าม commit ไฟล์ `.env`** ที่มี API key จริง ไฟล์นี้อยู่ใน `.gitignore` แล้ว

### 3.6 ห้าม `except Exception: pass`

เคยทำให้ `FishAPI` เรียก API ไม่สำเร็จมาตลอดโดยไม่มีใครรู้ (ดู `CHANGELOG.md` v0.2.1)
ให้ดัก error เป็นชนิดที่เจาะจง แล้วเก็บข้อความไว้ใน `last_error`

---

## 4. ก่อน commit ทุกครั้ง

```bash
python -m flake8 .
python -m pytest -q --cov=src --cov-report=term-missing
```

ทั้งสองคำสั่งต้องผ่าน **ชุดเดียวกับที่ GitHub Actions รันทุก push**
push สำเร็จไม่ได้แปลว่า CI ผ่าน — ถ้าหน้า commit บน GitHub ขึ้น ✕ ให้เปิด log ของ Actions ดูทันที

| เกณฑ์ | ค่าที่ต้องได้ |
|---|---|
| `flake8 .` | 0 issues (ความยาวบรรทัดไม่เกิน 100) |
| `pytest -q` | ผ่านทั้งหมด ไม่มี skip ที่ไม่ได้ตั้งใจ |
| เวลารันเทสต์ | ไม่เกิน 3 วินาที ถ้าช้ากว่านี้แปลว่ามีเคสรอเวลาจริงหรือรอเครือข่าย |

---

## 5. ปล่อยเวอร์ชันใหม่

1. แก้ `__version__` ใน `src/__init__.py` (ใช้ [Semantic Versioning](https://semver.org/lang/th/) — แก้บั๊กเพิ่มเลขท้าย เพิ่มฟีเจอร์เพิ่มเลขกลาง)
2. เพิ่มหัวข้อ `## [X.Y.Z]` ไว้**บนสุด**ของ `CHANGELOG.md` พร้อมตารางเวอร์ชันด้านบน
3. ตรวจในเครื่อง — `python tools/release.py check vX.Y.Z` ต้องขึ้น ✔
4. commit + push แล้ว `git tag vX.Y.Z` และ `git push origin vX.Y.Z`
5. ดูแท็บ Actions ว่า workflow **Release** ผ่าน แล้วตรวจหน้า Releases ว่ามี zip ของเวอร์ชันนั้น

ถ้า tag · `__version__` · CHANGELOG ไม่ตรงกัน workflow จะหยุดก่อนสร้าง release
ลบ tag ที่ผิดด้วย `git push --delete origin vX.Y.Z` แล้วแก้ให้ตรงก่อน tag ใหม่

---

## 6. รูปแบบ commit

```
<ประเภท>: <สิ่งที่ทำ>

feat: เพิ่มหน้าคลังสินค้าแบบตาราง
fix: แก้ .isdigit() ที่ยอมรับตัวยกแล้วทำให้ int() พัง
test: เพิ่มเคสทดสอบ API ล้มเหลว 4 แบบ
docs: อัปเดต README ให้ตรงกับสถาปัตยกรรมสอง API
```

---

## 7. ภาษาในโค้ด

| ส่วน | ภาษา |
|---|---|
| ชื่อตัวแปร ฟังก์ชัน คลาส | อังกฤษ |
| docstring และคอมเมนต์ | ไทย |
| ข้อความที่ผู้เล่นเห็น | ไทย |
| ข้อความใน `ValueError` | ไทย และต้องบอกวิธีแก้ ไม่ใช่แค่บอกว่าผิด |

คอมเมนต์ให้เขียนเฉพาะตอนที่ต้องอธิบาย **ว่าทำไม** ไม่ใช่อธิบายว่าโค้ดทำอะไร

---

## 8. บทบาทในทีม

บทบาท Planner และ Debugger/QA **หมุนเวียนทุกสปรินต์** ดูตารางว่าใครรับบทไหนได้ที่
[`PLAN.md`](PLAN.md) หัวข้อ 2
