"""ตรวจสอบความถูกต้องของข้อมูลนำเข้า (Sprint 1 — Front-End)

โมดูลนี้ไม่มี input() และไม่มี print() เพื่อให้ทดสอบด้วย pytest ได้โดยตรง
ทุกฟังก์ชันจะ raise ValueError พร้อมข้อความภาษาไทยเมื่อข้อมูลไม่ถูกต้อง
"""

BACK_COMMANDS = {"b", "back", "กลับ"}
QUIT_COMMANDS = {"q", "quit", "exit", "ออก"}


def normalize_command(raw_input):
    """ตัดช่องว่างหัวท้ายด้วย .strip() และแปลงเป็นตัวพิมพ์เล็กด้วย .lower()"""
    return str(raw_input).strip().lower()


def is_back_command(raw_input):
    """คืนค่า True เมื่อผู้ใช้สั่งย้อนกลับ (ไม่สนตัวพิมพ์เล็ก/ใหญ่)"""
    return normalize_command(raw_input) in BACK_COMMANDS


def is_quit_command(raw_input):
    """คืนค่า True เมื่อผู้ใช้สั่งออกจากโปรแกรม (ไม่สนตัวพิมพ์เล็ก/ใหญ่)"""
    return normalize_command(raw_input) in QUIT_COMMANDS


def validate_menu_choice(raw_input, min_option, max_option):
    """ตรวจสอบตัวเลือกเมนู คืนค่าเป็น int เมื่ออยู่ในช่วงที่กำหนด

    ปฏิเสธค่าว่าง ตัวอักษร ค่าติดลบ และทศนิยม โดยตรวจรูปแบบก่อนแปลงเป็น int
    เพราะ int("-5") ไม่ raise ValueError จึงพึ่ง try-except อย่างเดียวไม่ได้

    ใช้ .isdecimal() ไม่ใช่ .isdigit() เพราะ .isdigit() คืน True ให้ตัวยกอย่าง "²"
    ซึ่ง int() แปลงไม่ได้และจะทำให้โปรแกรมพัง ส่วนเลขไทยอย่าง "๑" ยังใช้ได้ตามปกติ
    """
    text = normalize_command(raw_input)

    if not text:
        raise ValueError("กรุณาพิมพ์ตัวเลือก ห้ามเว้นว่าง")

    if not text.isdecimal():
        raise ValueError(f"กรุณาเลือกเป็นตัวเลข {min_option} ถึง {max_option} เท่านั้น")

    choice = int(text)
    if choice < min_option or choice > max_option:
        raise ValueError(f"ตัวเลือกต้องอยู่ระหว่าง {min_option} ถึง {max_option}")

    return choice


def validate_qte_key(raw_input, expected_key):
    """ตรวจว่าผู้เล่นพิมพ์ตัวอักษรตรงกับโจทย์ของมินิเกมหรือไม่"""
    text = normalize_command(raw_input)

    if len(text) != 1:
        raise ValueError("กรุณาพิมพ์ตัวอักษรครั้งละหนึ่งตัว")

    return text == normalize_command(expected_key)


def validate_search_keyword(raw_input, max_length=30):
    """ตรวจคำค้นของหน้าคลังสินค้า — ห้ามว่าง และยาวไม่เกินที่กำหนด"""
    keyword = str(raw_input).strip()

    if not keyword:
        raise ValueError("คำค้นห้ามเว้นว่าง")

    if len(keyword) > max_length:
        raise ValueError(f"คำค้นต้องยาวไม่เกิน {max_length} ตัวอักษร")

    return keyword
