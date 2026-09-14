"""ส่วนแสดงผลทั้งหมดของ Sprint 1 (Presentation Layer)

แยกออกจาก validators.py ตาม pattern UI/Core separation
ไฟล์นี้มีเฉพาะ print() ไม่มีการคำนวณตรรกะของเกม
"""

LINE = "=" * 50
THIN_LINE = "-" * 50


def display_welcome_message():
    """แสดงแบนเนอร์ต้อนรับเมื่อเริ่มโปรแกรม"""
    print(LINE)
    print("        PixelPaw - Virtual Pet CLI (Sprint 1)")
    print("        Front-End Prototype : เมนู + ตรวจสอบอินพุต")
    print(LINE)
    print("พิมพ์ 'quit' ได้ทุกเมื่อเพื่อออกจากโปรแกรม")


def display_main_menu():
    """แสดงเมนูหลัก 4 ตัวเลือก"""
    print()
    print(LINE)
    print("                    เมนูหลัก")
    print(LINE)
    print("1. รับเลี้ยงน้องแมว (เลือกจากข้อมูลจำลอง)")
    print("2. ดูสถานะน้องแมว")
    print("3. เมนูดูแลน้องแมว")
    print("4. ออกจากโปรแกรม")
    print(LINE)


def display_breed_list(breeds):
    """แสดงรายการสายพันธุ์ที่เลือกได้"""
    print()
    print(LINE)
    print("               เลือกสายพันธุ์น้องแมว")
    print(LINE)
    for index, breed in enumerate(breeds, start=1):
        print(f"{index}. {breed['breed']} ({breed['country']})")
        print(f"   นิสัย        : {breed['temperament']}")
        print(f"   ความดื้อ     : {breed['stubbornness_score']} / 100")
        print(f"   รายละเอียด   : {breed['description']}")
        print(THIN_LINE)


def display_pet_status(pet):
    """แสดงสถานะน้องแมวที่เก็บอยู่ใน memory"""
    print()
    print(LINE)
    print(f"        สถานะของ {pet['name']} ({pet['breed']})")
    print(LINE)
    print(f"  อายุ                  : {pet['age']} ปี")
    print(f"  ประเทศถิ่นกำเนิด      : {pet['country']}")
    print(f"  ความหิว (Hunger)      : {pet['hunger']} / 100")
    print(f"  พลังงาน (Energy)      : {pet['energy']} / 100")
    print(f"  ความสุข (Happiness)   : {pet['happiness']} / 100")
    print(f"  คะแนนความดื้อ         : {pet['stubbornness_score']} / 100")
    print(LINE)


def display_care_menu(pet_name):
    """แสดงเมนูดูแลน้องแมว (Sprint 1 ยังเป็นโครงหน้าจอเท่านั้น)"""
    print()
    print(LINE)
    print(f"              เมนูดูแล {pet_name}")
    print(LINE)
    print("1. ให้อาหาร")
    print("2. เล่นกับน้องแมว")
    print("3. ให้น้องแมวนอนพัก")
    print("4. กลับสู่เมนูหลัก")
    print(LINE)


def display_pending_feature(action_name):
    """แจ้งว่าฟีเจอร์นี้เป็นขอบเขตของสปรินต์ถัดไป"""
    print(f"\n[Sprint 2] '{action_name}' จะเชื่อมตรรกะจริงในสปรินต์ถัดไป")


def display_error(message):
    """แสดงข้อความแจ้งเตือนเมื่ออินพุตไม่ถูกต้อง"""
    print(f"\n[X] {message}")


def display_info(message):
    """แสดงข้อความแจ้งข่าวทั่วไป"""
    print(f"\n[!] {message}")
