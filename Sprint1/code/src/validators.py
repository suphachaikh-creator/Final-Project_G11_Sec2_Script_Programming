"""ฟังก์ชันตรวจสอบความถูกต้องของอินพุต (Sprint 1 - Front-End)

โมดูลนี้ไม่มี input() และไม่มี print() เพื่อให้ทดสอบด้วย pytest ได้โดยตรง
ทุกฟังก์ชันจะ raise ValueError พร้อมข้อความภาษาไทยเมื่อข้อมูลไม่ถูกต้อง
"""

STAT_MIN = 0
STAT_MAX = 100

QUIT_COMMANDS = {"quit", "exit", "q", "ออก"}

MAX_NAME_LENGTH = 20


def normalize_command(raw_input):
    """ตัดช่องว่างหัวท้ายด้วย .strip() และแปลงเป็นตัวพิมพ์เล็กด้วย .lower()"""
    return str(raw_input).strip().lower()


def is_quit_command(raw_input):
    """คืนค่า True เมื่อผู้ใช้พิมพ์คำสั่งออกจากโปรแกรม (ไม่สนตัวพิมพ์เล็ก/ใหญ่)"""
    return normalize_command(raw_input) in QUIT_COMMANDS


def validate_menu_choice(raw_input, min_option, max_option):
    """ตรวจสอบตัวเลือกเมนู คืนค่าเป็น int เมื่ออยู่ในช่วงที่กำหนด"""
    text = normalize_command(raw_input)

    if not text:
        raise ValueError("กรุณาพิมพ์ตัวเลือก ห้ามเว้นว่าง")

    if not text.isdigit():
        raise ValueError(f"กรุณาเลือกเป็นตัวเลข {min_option} ถึง {max_option} เท่านั้น")

    choice = int(text)
    if choice < min_option or choice > max_option:
        raise ValueError(f"ตัวเลือกต้องอยู่ระหว่าง {min_option} ถึง {max_option}")

    return choice


def validate_pet_name(raw_input):
    """ตรวจสอบชื่อน้องแมว: ห้ามว่าง และยาวไม่เกิน MAX_NAME_LENGTH ตัวอักษร"""
    name = str(raw_input).strip()

    if not name:
        raise ValueError("ชื่อน้องแมวห้ามเว้นว่าง")

    if len(name) > MAX_NAME_LENGTH:
        raise ValueError(f"ชื่อน้องแมวต้องยาวไม่เกิน {MAX_NAME_LENGTH} ตัวอักษร")

    return name


def validate_age(raw_input):
    """ตรวจสอบอายุน้องแมว: ต้องเป็นจำนวนเต็มบวก (0 ถึง 30 ปี)"""
    text = str(raw_input).strip()

    if not text:
        raise ValueError("อายุห้ามเว้นว่าง")

    if not text.isdigit():
        raise ValueError("อายุต้องเป็นจำนวนเต็มบวกเท่านั้น")

    age = int(text)
    if age > 30:
        raise ValueError("อายุต้องไม่เกิน 30 ปี")

    return age


def clamp_stat(value):
    """บีบค่าสถานะให้อยู่ในช่วง 0-100 เสมอ ใช้ป้องกันค่าเพี้ยนตอนแสดงผล"""
    return max(STAT_MIN, min(STAT_MAX, value))
