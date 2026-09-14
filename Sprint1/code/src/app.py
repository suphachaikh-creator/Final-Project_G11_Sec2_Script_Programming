"""PixelPaw - Virtual Pet CLI (Sprint 1: Front-End App Dev)

ขอบเขตของสปรินต์นี้คือหน้าจอ CLI, ระบบเมนู และการตรวจสอบอินพุตเท่านั้น
ข้อมูลทั้งหมดเก็บอยู่ใน memory ยังไม่เรียก API จริงและยังไม่บันทึกไฟล์จริง
(ส่วนดังกล่าวเป็นขอบเขตของ Sprint 2)
"""

from src import ui
from src.mock_data import MOCK_BREEDS, build_mock_pet
from src.validators import (
    is_quit_command,
    validate_age,
    validate_menu_choice,
    validate_pet_name,
)

MAIN_MENU_MIN = 1
MAIN_MENU_MAX = 4
CARE_MENU_MIN = 1
CARE_MENU_MAX = 4

CARE_ACTIONS = {
    1: "ให้อาหาร",
    2: "เล่นกับน้องแมว",
    3: "ให้น้องแมวนอนพัก",
}


def get_command_input(prompt):
    """รับอินพุตจากผู้ใช้ พร้อมตัดช่องว่างหัวท้าย

    ถ้าสตรีมอินพุตปิดลง (เช่น รันแบบ pipe) จะถือว่าผู้ใช้สั่งออกจากโปรแกรม
    """
    try:
        return input(prompt).strip()
    except EOFError:
        return "quit"


def prompt_until_valid(prompt, validator):
    """ถามซ้ำจนกว่าอินพุตจะผ่านการตรวจสอบ คืนค่า None เมื่อผู้ใช้สั่ง quit"""
    while True:
        raw_input_value = get_command_input(prompt)

        if is_quit_command(raw_input_value):
            return None

        try:
            return validator(raw_input_value)
        except ValueError as error:
            ui.display_error(str(error))


def choose_breed():
    """ให้ผู้ใช้เลือกสายพันธุ์จากข้อมูลจำลอง คืนค่า None เมื่อยกเลิก"""
    ui.display_breed_list(MOCK_BREEDS)
    prompt = f"เลือกหมายเลขสายพันธุ์ (1-{len(MOCK_BREEDS)}): "
    choice = prompt_until_valid(
        prompt,
        lambda value: validate_menu_choice(value, 1, len(MOCK_BREEDS)),
    )

    if choice is None:
        return None

    return MOCK_BREEDS[choice - 1]


def adopt_pet():
    """ขั้นตอนรับเลี้ยงน้องแมว: เลือกสายพันธุ์ -> ตั้งชื่อ -> ระบุอายุ"""
    breed = choose_breed()
    if breed is None:
        return None

    name = prompt_until_valid("ตั้งชื่อให้น้องแมว: ", validate_pet_name)
    if name is None:
        return None

    age = prompt_until_valid("ระบุอายุน้องแมว (ปี): ", validate_age)
    if age is None:
        return None

    return build_mock_pet(name, age, breed)


def run_care_menu(pet):
    """เมนูดูแลน้องแมว - Sprint 1 แสดงผลอย่างเดียว ยังไม่คำนวณค่าสถานะ"""
    while True:
        ui.display_care_menu(pet["name"])
        raw_input_value = get_command_input(f"กรุณาเลือกคำสั่ง ({CARE_MENU_MIN}-{CARE_MENU_MAX}): ")

        if is_quit_command(raw_input_value):
            return

        try:
            choice = validate_menu_choice(raw_input_value, CARE_MENU_MIN, CARE_MENU_MAX)
        except ValueError as error:
            ui.display_error(str(error))
            continue

        if choice == CARE_MENU_MAX:
            ui.display_info("กลับสู่เมนูหลัก")
            return

        ui.display_pending_feature(CARE_ACTIONS[choice])


def run_app():
    """ลูปหลักของแอปพลิเคชัน"""
    ui.display_welcome_message()
    pet = None

    while True:
        ui.display_main_menu()
        raw_input_value = get_command_input(f"กรุณาเลือกเมนู ({MAIN_MENU_MIN}-{MAIN_MENU_MAX}): ")

        if is_quit_command(raw_input_value):
            break

        try:
            choice = validate_menu_choice(raw_input_value, MAIN_MENU_MIN, MAIN_MENU_MAX)
        except ValueError as error:
            ui.display_error(str(error))
            continue

        if choice == 1:
            new_pet = adopt_pet()
            if new_pet is None:
                ui.display_info("ยกเลิกการรับเลี้ยงน้องแมว")
            else:
                pet = new_pet
                ui.display_info(f"รับเลี้ยง '{pet['name']}' เรียบร้อย (เก็บไว้ใน memory)")
                ui.display_pet_status(pet)

        elif choice == 2:
            if pet is None:
                ui.display_error("ยังไม่มีน้องแมว กรุณาเลือกเมนู 1 ก่อน")
            else:
                ui.display_pet_status(pet)

        elif choice == 3:
            if pet is None:
                ui.display_error("ยังไม่มีน้องแมว กรุณาเลือกเมนู 1 ก่อน")
            else:
                run_care_menu(pet)

        else:
            break

    ui.display_info("ขอบคุณที่ทดลองใช้ PixelPaw! แล้วพบกันใหม่")
