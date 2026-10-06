# UML Class Diagram — HOW_DO_YOU_FISH

แผนผังนี้สร้างจากโค้ดจริงในเวอร์ชันปัจจุบัน ไม่ใช่ผังที่วาดไว้ตอนต้นเทอมแล้วไม่ได้อัปเดต
GitHub แสดงผล Mermaid ได้ในตัว จึงเปิดดูได้ทันทีโดยไม่ต้องติดตั้งอะไรเพิ่ม

---

## 1. ชั้นโดเมนและตรรกะของเกม

คลาสกลุ่มนี้ไม่รู้จักหน้าจอ ไฟล์ และเครือข่ายเลย จึงเขียน unit test ได้ครบทุกเมธอด

```mermaid
classDiagram
    direction LR

    class GameState {
        +money: int
        +inventory: list~Fish~
        +bait_level: int
        +rod_level: int
        +quest_data: dict
        +difficulty_data: dict
        +bait_cost
        +rod_cost
        +can_afford(cost)
        +add_fish(fish)
        +require_fish(fish)
        +rename_fish(fish, new_name)
        +set_keep(fish, keep)
        +toggle_keep(fish)
        +kept_fish()
        +sell_all()
        +sell_fish(fish)
        +sell_species(name)
        +count_species(name)
        +upgrade_bait()
        +upgrade_rod()
        +search_inventory(keyword)
        +filter_inventory(location)
        +sort_inventory(key, descending)
        +summary()
        +to_dict()
        +from_dict(data)$
    }

    class Fish {
        +name: str
        +location: str
        +weight_kg: float
        +price: int
        +keep: bool
        +roll_weight(bait_level, rng)$
        +price_for(weight_kg, bait_level)$
        +catch(name, location, bait_level, rng)$
        +to_dict()
        +from_dict(data)$
    }

    class NotEnoughMoneyError {
        <<Exception>>
    }

    class FishNotFoundError {
        <<Exception>>
    }

    class FishProtectedError {
        <<Exception>>
    }

    class QTEMinigame {
        -rng
        -clock
        +targets: list
        +time_limit: float
        +hit_count: int
        +miss_count: int
        +current_target
        +is_complete
        +start()
        +submit(key)
        +time_left()
        +is_timed_out()
        +result()
        +time_limit_for(rod_level)$
    }

    class DifficultyTuner {
        +rounds: list
        +record(result)
        +hit_rate()
        +level()
        +time_limit_for(rod_level)
        +target_length_for(rod_level)
        +settings_for(rod_level)
        +apply_to(minigame, rod_level, rng)
        +to_dict()
        +from_dict(data)$
    }

    class AIFishingAgent {
        -state: GameState
        -rng
        +quests: list
        +ai_checked: bool
        +ai_connected: bool
        +gemini_configured
        +daily_quests(today)
        +generate_local_quests(today)
        +generate_gemini_quests(today, apply, force)
        +record_catch(fish)
        +claim_reward(quest_id)
        +choose_species(api, location, rng)
        +quest_description(quest)$
    }

    GameState o-- Fish : ถือปลาในกระเป๋า
    GameState ..> NotEnoughMoneyError : โยนเมื่อเงินไม่พอ
    GameState ..> FishNotFoundError : อ้างถึงปลาที่ไม่มีในกระเป๋า
    GameState ..> FishProtectedError : ขายปลาที่ทำเครื่องหมายเก็บไว้
    ValueError <|-- FishNotFoundError
    ValueError <|-- FishProtectedError
    DifficultyTuner ..> QTEMinigame : ปรับเวลาและความยาวโจทย์
    AIFishingAgent --> GameState : อ่านเลเวล เก็บเควสต์ จ่ายรางวัล
    DifficultyTuner ..> GameState : เก็บประวัติใน difficulty_data
```

`AIFishingAgent` (v0.7.0) เรียก Gemini ได้แบบไม่บังคับ ถ้าเรียกไม่ได้จะสุ่มเควสต์ในเครื่อง
ส่วน `DifficultyTuner` (v1.0.0) ปรับเวลาและความยาวโจทย์จากภายนอกโดยไม่แก้ `QTEMinigame`
ทั้งสองคลาสเก็บข้อมูลไว้ใน `GameState` จึงบันทึกลงไฟล์เซฟเดียวกันกับเงินและกระเป๋าปลา

---

## 2. ชั้นเชื่อมต่อข้อมูลและไฟล์

```mermaid
classDiagram
    direction TB

    class FishAPI {
        -worms: WormsAPI
        -openfisheries: OpenFisheriesAPI
        +last_error: str
        +using_fallback: bool
        +enriched_count: int
        +fetch_species(location)
        +random_species(location, rng)
        +local_species(location)$
    }

    class WormsAPI {
        -http
        +last_error: str
        +search_by_vernacular(word)
        +fetch_fish_records()
    }

    class OpenFisheriesAPI {
        -http
        +last_error: str
        +fetch_common_names()
    }

    class SpeciesLoader {
        -api: FishAPI
        -spawn
        +ready: set
        +started: bool
        +is_complete
        +using_fallback
        +start()
        +is_ready(location)
        +status()
        +status_text()
        +random_species(location, rng)
    }

    class SaveManager {
        +save_file: str
        +last_error: str
        +exists()
        +save(state)
        +load()
        +load_or_new()
    }

    class CatchLog {
        +log_file: str
        +last_error: str
        +skipped: int
        -clock
        +record(fish)
        +entries()
        +summary()
    }

    class UpdateChecker {
        -http
        -spawn
        +current: str
        +latest: str
        +status: str
        +url: str
        +last_error: str
        +start()
        +check()
        +is_complete
        +update_available
        +status_text()
    }

    FishAPI *-- WormsAPI : แหล่งน้ำ + อนุกรมวิธาน
    FishAPI *-- OpenFisheriesAPI : ชื่อสามัญ
    SpeciesLoader o-- FishAPI : ห่อไว้ไม่ให้หน้าต่างค้าง
```

`SpeciesLoader` มีหน้าตาเหมือน `FishAPI` ตรงที่มี `random_species()` และ `using_fallback`
จึงส่งเข้าไปแทนกันได้โดยไม่ต้องแก้ชั้นที่เรียกใช้

`UpdateChecker` (v1.0.0) ถาม GitHub Releases ในเบื้องหลังเหมือน `SpeciesLoader`
และมี `is_complete` เหมือนกัน `FishingApp` จึงรอทั้งสองตัวด้วยลูปเดียวกันก่อนรีเฟรชหน้าแรก

`CatchLog` (v1.0.0) เขียนต่อท้าย `data/catch_log.jsonl` บรรทัดละหนึ่งตัว
ส่วน `summarize()` เป็นฟังก์ชันล้วนระดับโมดูลที่สรุปสถิติจากรายการประวัติ

---

## 3. ชั้นหน้าจอ

`presenter.py` ตัดสินใจ ส่วนไฟล์ใน `pages/` วาด (หน้าละหนึ่งไฟล์) แยกกันเพื่อให้เทสต์รันบนเครื่องที่ไม่มีจอได้

```mermaid
classDiagram
    direction TB

    class FishingApp {
        -state_data: GameState
        -api: SpeciesLoader
        -saver: SaveManager
        -ai_agent: AIFishingAgent
        -tuner: DifficultyTuner
        -catch_log: CatchLog
        -updates: UpdateChecker
        -clock: TkClock
        +game
        +show_frame(name)
        +autosave()
        +refresh_sidebar()
        +start_loading()
        +bind_keys(handler)
        +tick()
        +on_close()
    }

    class TkClock {
        +interval: float
        +now: float
        +tick()
    }

    class DashboardPresenter {
        -state: GameState
        -catch_log: CatchLog
        -updates: UpdateChecker
        +status_lines()
        +api_status()
        +history_lines()
        +version_text()
        +can_download_update()
    }

    class FishingPresenter {
        -state: GameState
        -api
        -clock
        -ai_agent: AIFishingAgent
        -tuner: DifficultyTuner
        -catch_log: CatchLog
        +minigame: QTEMinigame
        +is_running
        +start(location)
        +press(key)
        +finish()
        +target_text()
        +timer_text()
        +progress_ratio()
        +difficulty_text()
    }

    class ShopPresenter {
        -state: GameState
        +items()
        +buy(key)
    }

    class InventoryPresenter {
        -state: GameState
        +keyword: str
        +location_filter: str
        +sort_key: str
        +descending: bool
        +toggle_sort(key)
        +heading_text(key)
        +visible_fish()
        +visible_rows()
        +summary_lines()
        +fish_at(index)
        +species_count_at(index)
        +rename_at(index, new_name)
        +toggle_keep_at(index)
        +keep_label_at(index)
        +sell_one(index)
        +sell_species_at(index)
        +sell_all()
    }

    class BaseFrame {
        <<abstract>>
        +title: str
        +subtitle: str
        +on_show()
    }

    class DashboardFrame {
        +refresh_status()
        +open_download_page()
    }
    class QuestFrame {
        +refresh_quests()
        +check_ai_connection()
        +test_gemini_api()
        +claim_reward(quest_id)
    }
    class FishingFrame {
        +start()
        +on_key(event)
        +refresh()
        +finish()
    }
    class ShopFrame {
        +buy(key)
    }
    class InventoryFrame {
        +selected_index()
        +update_sell_buttons()
        +rename()
        +toggle_keep()
        +after_change()
        +sell_one()
        +sell_species()
        +sell()
    }

    FishingApp *-- TkClock
    FishingApp o-- BaseFrame : ถือ 5 เฟรม
    BaseFrame <|-- DashboardFrame
    BaseFrame <|-- FishingFrame
    BaseFrame <|-- QuestFrame
    BaseFrame <|-- ShopFrame
    BaseFrame <|-- InventoryFrame

    DashboardFrame --> DashboardPresenter : ถามว่าจะแสดงอะไร
    FishingFrame --> FishingPresenter
    QuestFrame --> AIFishingAgent : เรียก Gemini ในเธรดเบื้องหลัง
    ShopFrame --> ShopPresenter
    InventoryFrame --> InventoryPresenter
```

### วิดเจ็ตที่วาดเอง

Tkinter ไม่มีรูปทรงเหล่านี้มาให้ จึงวาดเองด้วย `Canvas` ใน `src/gui/widgets.py`

```mermaid
classDiagram
    class Card {
        การ์ดพื้นอ่อนพร้อมหัวข้อ
    }
    class StatTile {
        +set(text)
    }
    class TimerBar {
        +set(ratio)
    }
    class KeycapRow {
        +show(letters, done)
        +clear()
    }
```

`TimerBar` เปลี่ยนสีตามเวลาที่เหลือ (เขียว → ทอง → แดง) ผ่าน `theme.time_color()`
ส่วน `KeycapRow` ทำให้ตัวอักษรที่ต้องกดตอนนี้เรืองสีหลัก

### โหมดสำรองแบบ Terminal

`FishingCLI` ใน `src/cli.py` เป็นชั้นแสดงผลอีกตัวที่ยังคงไว้จาก Sprint 1-2
เรียกใช้ `GameState` · `QTEMinigame` · `FishAPI` ชุดเดียวกับ GUI ทุกประการ
เปิดด้วย `python main.py --cli` และ `main.py` จะถอยมาใช้ตัวนี้เองถ้าเปิดหน้าต่างไม่ได้

```mermaid
classDiagram
    class FishingCLI {
        -state: GameState
        -api: FishAPI
        -saver: SaveManager
        +run()
        +ask_menu(prompt, min, max)
        +fishing_screen(location)
        +shop_screen()
        +inventory_screen()
    }
```

---

## 4. การแบ่งชั้น

```mermaid
flowchart TB
    subgraph P["Presentation — ไม่มีกฎของเกม"]
        A1["gui/app.py · gui/pages/"]
        A2["gui/theme.py · gui/widgets.py"]
        A3["ui.py (โหมด CLI)"]
    end

    subgraph AP["Application — ตัดสินใจ"]
        B1["gui/presenter.py"]
        B2["gui/species_loader.py"]
        B3["cli.py"]
    end

    subgraph V["Validation"]
        C1["validators.py"]
    end

    subgraph D["Domain — ตรรกะบริสุทธิ์"]
        D1["game_state.py"]
        D2["fish.py"]
        D3["minigame.py"]
        D4["ai_fishing.py"]
        D5["difficulty.py"]
    end

    subgraph I["Integration — เครือข่าย"]
        E1["worms_api.py"]
        E2["openfisheries_api.py"]
        E3["fish_api.py"]
        E4["update_checker.py"]
    end

    subgraph DA["Data Access — ไฟล์"]
        F1["save_manager.py"]
        F2["catch_log.py"]
    end

    P --> AP
    AP --> V
    AP --> D
    AP --> I
    AP --> DA
    B2 --> E3
    E3 --> E1
    E3 --> E2
```

ลูกศรชี้ทางเดียวลงล่างเสมอ ชั้นล่างไม่รู้จักชั้นบน
`game_state.py` จึงไม่รู้ว่ามีหน้าจอ และ `fish.py` ไม่รู้ว่ามี API
`ai_fishing.py` เป็นข้อยกเว้นเดียวที่ชั้นโดเมนเรียกเครือข่ายเอง (Gemini) แต่ไม่ import tkinter
และทุกเส้นทางที่เรียกไม่สำเร็จมีโหมดสำรอง

---

## 5. จุดที่ฉีดของเข้ามาจากภายนอก (Dependency Injection)

จุดที่ทดสอบยากที่สุดคือ **เครือข่าย เวลา การสุ่ม และเธรด** ทั้งหมดถูกออกแบบให้แทนที่ได้
ตั้งแต่ตอนเขียนโค้ด ไม่ใช่มาแก้ทีหลัง

| คลาส | สิ่งที่ฉีดเข้ามา | ตอนเล่นจริง | ตอนทดสอบ |
|---|---|---|---|
| `WormsAPI` · `OpenFisheriesAPI` | `http` | โมดูล `requests` | `FakeHttp` |
| `FishAPI` | `worms` · `openfisheries` | ตัวจริง | `FakeWorms` · `FakeOpenFisheries` |
| `SpeciesLoader` | `spawn` | `threading.Thread` | `ManualSpawn` ที่สั่งรันเองได้ |
| `QTEMinigame` | `clock` | `TkClock` (GUI) หรือ `time.monotonic` (CLI) | นาฬิกาจำลอง |
| `QTEMinigame` · `Fish` | `rng` | โมดูล `random` | `FakeRng` ที่คืนค่าเดิมทุกครั้ง |
| `AIFishingAgent` | `rng` · `requests.post` · `GEMINI_API_KEY` | โมดูล `random` · Gemini จริง · ค่าใน `.env` | ตัวสุ่มปลอม · `FakePost` ผ่าน `monkeypatch` · ลบ key ออก |
| `FishingPresenter` | `ai_agent` · `tuner` | ตัวจริงจาก `FishingApp` | ไม่ส่ง (ต้องเล่นได้เหมือนเดิม) หรือส่งตัวจริงพร้อมข้อมูลกำหนดเอง |
| `SaveManager` | `save_file` | ไฟล์ใน `data/` | `tmp_path` ของ pytest |
| `CatchLog` | `log_file` · `clock` | `data/catch_log.jsonl` · เวลาจริง | `tmp_path` · นาฬิกาที่คืนเวลาคงที่ |
| `UpdateChecker` | `http` · `spawn` · `current` | `requests` · `threading.Thread` · `src.__version__` | `FakeHttp` · `spawn` ที่เก็บงานไว้สั่งรันเอง · เวอร์ชันที่กำหนดเอง |
| `FishingApp` | `state` · `api` · `saver` | ของจริงทั้งหมด | สถานะและตัวเซฟปลอมใน smoke test |

ผลคือชุดทดสอบทั้งหมดรันแบบออฟไลน์ ไม่แตะไฟล์จริง ไม่รอเวลาจริง
ไม่สร้างเธรดจริง และไม่เปิดหน้าต่างจริง

---

## 6. เส้นทางของข้อมูลหนึ่งรอบการเล่น

```mermaid
sequenceDiagram
    participant ผู้เล่น
    participant FishingFrame
    participant FishingPresenter
    participant DifficultyTuner
    participant QTEMinigame
    participant AIFishingAgent
    participant SpeciesLoader
    participant GameState
    participant CatchLog

    ผู้เล่น->>FishingFrame: กดปุ่ม "เริ่มตกปลา"
    FishingFrame->>FishingPresenter: start(location)
    FishingPresenter->>QTEMinigame: สร้างพร้อมฉีด clock
    FishingPresenter->>DifficultyTuner: apply_to(minigame, rod_level)
    DifficultyTuner-->>QTEMinigame: ตั้งเวลาและความยาวโจทย์

    loop ทุก 100 มิลลิวินาที
        FishingFrame->>FishingPresenter: refresh()
        FishingPresenter->>QTEMinigame: time_left()
    end

    ผู้เล่น->>FishingFrame: พิมพ์ตัวอักษร
    FishingFrame->>FishingPresenter: press(key)
    FishingPresenter->>QTEMinigame: submit(key)

    FishingPresenter->>AIFishingAgent: choose_species(api, location)
    AIFishingAgent->>SpeciesLoader: random_species(location) × 3
    Note over SpeciesLoader: ไม่รอเครือข่าย<br/>ยังโหลดไม่เสร็จก็ใช้ข้อมูลสำรอง
    AIFishingAgent-->>FishingPresenter: ชนิดที่มีในกระเป๋าน้อยที่สุด
    FishingPresenter->>GameState: add_fish(fish)
    FishingPresenter->>AIFishingAgent: record_catch(fish)
    AIFishingAgent->>GameState: quest_data (ความคืบหน้าเควสต์)
    FishingPresenter->>DifficultyTuner: record(result)
    FishingPresenter->>GameState: difficulty_data = tuner.to_dict()
    FishingPresenter->>CatchLog: record(fish) — ต่อท้าย catch_log.jsonl
    FishingPresenter-->>FishingFrame: ข้อความสรุปผล
    FishingFrame->>FishingApp: autosave() — ปลา เควสต์ และความยากลงไฟล์เดียวกัน
```

---

## 7. เส้นทางการขายปลา

```mermaid
sequenceDiagram
    participant ผู้เล่น
    participant InventoryFrame
    participant InventoryPresenter
    participant GameState

    ผู้เล่น->>InventoryFrame: คลิกแถวในตาราง
    InventoryFrame->>InventoryPresenter: fish_at(index)
    InventoryPresenter->>InventoryPresenter: visible_fish() — ลำดับตรงกับตารางเสมอ
    InventoryPresenter-->>InventoryFrame: ปลาที่เลือก
    InventoryFrame->>InventoryPresenter: species_count_at(index)
    InventoryFrame-->>ผู้เล่น: เปิดปุ่ม · ขึ้นว่า "ขายทั้งชนิดนี้ (3 ตัว)"

    alt ขายทีละตัว
        ผู้เล่น->>InventoryFrame: กด "ขายตัวที่เลือก"
        InventoryFrame->>InventoryPresenter: sell_one(index)
        InventoryPresenter->>GameState: sell_fish(fish)
        Note over GameState: เทียบด้วยตัวตนของอ็อบเจกต์<br/>ปลาชื่อซ้ำกันจึงขายผิดตัวไม่ได้
    else ขายยกชนิด
        ผู้เล่น->>InventoryFrame: กด "ขายทั้งชนิดนี้"
        InventoryFrame->>InventoryPresenter: sell_species_at(index)
        InventoryPresenter->>GameState: sell_species(name)
        Note over GameState: ข้ามตัวที่ทำเครื่องหมายเก็บไว้
    end

    alt ปลาถูกเก็บไว้ไม่ขาย
        GameState-->>InventoryPresenter: FishProtectedError
        InventoryPresenter-->>InventoryFrame: ข้อความเตือน ไม่ใช่ crash
    else ขายได้
        GameState-->>InventoryPresenter: เงินที่ได้รับ
        InventoryPresenter-->>InventoryFrame: ข้อความผลลัพธ์
    end

    InventoryFrame->>InventoryFrame: after_change()
    InventoryFrame->>FishingApp: autosave() — เขียนไฟล์เซฟทันที
```

---

## 8. เส้นทางการแก้ไขข้อมูลปลา (Update)

ส่วน **U** ของ CRUD เพิ่มใน Sprint 3 — การตรวจชื่ออยู่ชั้น Validation
ส่วนกฎว่าปลาตัวไหนแก้ได้อยู่ชั้น Domain หน้าจอไม่ตัดสินใจเองเลย

```mermaid
sequenceDiagram
    participant ผู้เล่น
    participant InventoryFrame
    participant InventoryPresenter
    participant validators
    participant GameState
    participant FishingApp

    ผู้เล่น->>InventoryFrame: พิมพ์ชื่อเล่นแล้วกด "เปลี่ยนชื่อ"
    InventoryFrame->>InventoryPresenter: rename_at(index, new_name)
    InventoryPresenter->>validators: validate_fish_name(new_name)

    alt ชื่อว่าง · ยาวเกิน 24 · มีอักขระขึ้นบรรทัดใหม่
        validators-->>InventoryPresenter: ValueError
        InventoryPresenter-->>InventoryFrame: ข้อความเตือน ชื่อไม่ถูกเปลี่ยน
    else ชื่อใช้ได้
        validators-->>InventoryPresenter: ชื่อที่ตัดช่องว่างแล้ว
        InventoryPresenter->>GameState: rename_fish(fish, name)
        GameState->>GameState: require_fish(fish)
        Note over GameState: ไม่อยู่ในกระเป๋า → FishNotFoundError
        GameState-->>InventoryPresenter: ชื่อใหม่
    end

    ผู้เล่น->>InventoryFrame: กด "เก็บไว้ไม่ขาย"
    InventoryFrame->>InventoryPresenter: toggle_keep_at(index)
    InventoryPresenter->>GameState: toggle_keep(fish)
    GameState-->>InventoryPresenter: สถานะใหม่
    InventoryPresenter-->>InventoryFrame: แถวขึ้นดาวนำหน้าชื่อ

    InventoryFrame->>FishingApp: autosave() — ไฟล์เซฟตรงกับหน้าจอเสมอ
```

---

## 9. จังหวะการบันทึกไฟล์

ข้อกำหนดคือข้อมูลในหน่วยความจำต้องตรงกับไฟล์ตลอดเวลา
จึงเขียนลงไฟล์**ทันทีที่สถานะเปลี่ยน** ไม่ใช่รอตอนปิดโปรแกรม

| เหตุการณ์ | ผู้เรียก |
|---|---|
| จับปลาได้ | `FishingFrame.finish()` |
| ซื้อของสำเร็จ | `ShopFrame.buy()` |
| ขาย · เปลี่ยนชื่อ · เก็บไว้ไม่ขาย | `InventoryFrame.after_change()` |
| รับรางวัลเควสต์ · ได้ชุดเควสต์ใหม่ | `QuestFrame.claim_reward()` · `QuestFrame.refresh_quests()` |
| ปิดหน้าต่าง | `FishingApp.on_close()` |

ทุกช่องเรียก `FishingApp.autosave()` ตัวเดียวกัน จุดบันทึกจึงอยู่ที่เดียว
ไม่กระจายไปตามเฟรม และเพราะ `quest_data` กับ `difficulty_data` อยู่ใน `GameState`
การบันทึกครั้งเดียวจึงเขียนเงิน กระเป๋าปลา เควสต์ และประวัติความยากลง `save_game.json` พร้อมกัน
เงินรางวัลกับเครื่องหมาย "รับรางวัลแล้ว" จึงไม่มีทางอยู่คนละไฟล์จนกดรับซ้ำได้

ข้อยกเว้นเดียวคือ `catch_log.jsonl` ที่ `FishingPresenter.finish()` ต่อท้ายทันทีที่จับได้
เพราะเป็นบันทึกเหตุการณ์ที่ไม่มีค่าใดในไฟล์เซฟอ้างอิงถึง
