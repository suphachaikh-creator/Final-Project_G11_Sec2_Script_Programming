"""เมนูหลักของ Virtual Pet App (Sprint 2: Back-End + Full-Stack)

สปรินต์นี้เชื่อมทั้ง API จริง, ไฟล์ JSON จริง และตรรกะการเลี้ยงจริง
ส่วนหน้าจอ CLI พื้นฐานพัฒนาไว้แล้วในโฟลเดอร์ Sprint1
"""

import time

from src.app_functions import fetch_new_pets, load_game, save_game
from src.game import start_game_loop
from src.pet import Pet

DEFAULT_PET_NAME = "น้องเหมียว"


def display_breeds(cats):
    """แสดงรายการสายพันธุ์ที่ดึงมาจาก API"""
    print("\n" + "=" * 15 + " เลือกสายพันธุ์แมวของคุณ " + "=" * 15)
    for index, cat in enumerate(cats, start=1):
        print(f"{index}. สายพันธุ์: {cat.get('breed')} ({cat.get('country')})")
        print(f"   นิสัย: {cat.get('temperament')}")
        print(f"   คะแนนความดื้อ: {cat.get('stubbornness_score')} / 100")
        print(f"   รายละเอียด: {cat.get('description')}")
        print("-" * 45)


def create_pet_from_breed(selected_cat, pet_name):
    """สร้างอ็อบเจกต์ Pet จากข้อมูลสายพันธุ์ที่ผู้ใช้เลือก"""
    return Pet(
        name=pet_name or DEFAULT_PET_NAME,
        breed=selected_cat.get("breed"),
        country=selected_cat.get("country"),
        temperament=selected_cat.get("temperament"),
        stubbornness_score=selected_cat.get("stubbornness_score", 50),
        description=selected_cat.get("description"),
    )


def start_new_game():
    """เริ่มเกมใหม่: ดึงสายพันธุ์จาก API -> เลือก -> ตั้งชื่อ -> บันทึก"""
    print("\nกำลังเชื่อมต่อ API เพื่อเลือกสายพันธุ์แมว...")
    cats = fetch_new_pets()

    if not cats:
        print("\n[X] ไม่สามารถดึงข้อมูลจาก API ได้ กรุณาตรวจสอบอินเทอร์เน็ตหรือ GEMINI_API_KEY")
        time.sleep(1.5)
        return

    display_breeds(cats)
    sub_choice = input(f"เลือกหมายเลขสายพันธุ์ (1-{len(cats)}): ").strip()

    if not (sub_choice.isdigit() and 1 <= int(sub_choice) <= len(cats)):
        print("\n[X] ตัวเลือกไม่ถูกต้อง")
        time.sleep(1)
        return

    pet_name = input("ตั้งชื่อให้น้องแมวของคุณ: ").strip()
    pet = create_pet_from_breed(cats[int(sub_choice) - 1], pet_name)

    save_game(pet)
    print(f"\n[!] สร้างน้องแมว '{pet.name}' สำเร็จ! เริ่มต้นเลี้ยงกันเลย")
    time.sleep(1.5)
    start_game_loop(pet)


def continue_game(missing_message):
    """โหลดเซฟแล้วเข้าสู่ลูปการเลี้ยง ถ้าไม่มีเซฟจะแจ้งเตือน"""
    pet = load_game()

    if pet is None:
        print(f"\n[!] {missing_message}")
        time.sleep(1.5)
        return

    print(f"\n[!] โหลดข้อมูลของ {pet.name} สำเร็จ!")
    time.sleep(1)
    start_game_loop(pet)


def main_menu():
    """ลูปเมนูหลักของแอปพลิเคชัน"""
    while True:
        print("\n" + "=" * 45)
        print("         VIRTUAL PET APP - เมนูหลัก")
        print("=" * 45)
        print("1. เล่นต่อ (โหลดจากเซฟล่าสุด)")
        print("2. เริ่มใหม่ (ดึงข้อมูลสายพันธุ์จาก API)")
        print("3. โหลด (ตรวจสอบและดึงข้อมูลจาก data/pet_state.json)")
        print("4. ออกจากโปรแกรม")
        print("=" * 45)

        choice = input("กรุณาเลือกเมนู (1-4): ").strip()

        if choice == "1":
            continue_game("ไม่พบเซฟเกมล่าสุด! กรุณาเลือก 'เริ่มใหม่' หรือ 'โหลด' ก่อน")
        elif choice == "2":
            start_new_game()
        elif choice == "3":
            continue_game("ไม่พบไฟล์ข้อมูลเซฟใน data/pet_state.json")
        elif choice == "4":
            print("\nขอบคุณที่เล่น Virtual Pet App! ไว้พบกันใหม่...")
            break
        else:
            print("\n[X] กรุณาเลือกตัวเลข 1 ถึง 4 เท่านั้น")
            time.sleep(1)
