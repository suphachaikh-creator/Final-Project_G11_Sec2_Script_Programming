"""ลูปการเลี้ยงน้องแมว เชื่อมตรรกะของคลาส Pet เข้ากับหน้าจอ (Sprint 2)"""

import time

from src.app_functions import save_game


def render_status(pet):
    """แสดงสถานะปัจจุบันของน้องแมว"""
    print("\n" + "=" * 45)
    print(f" หน้าจอเลี้ยงน้องแมว: {pet.name} ({pet.breed})")
    print("=" * 45)
    print(f"  ความหิว (Hunger)    : {pet.hunger} / 100")
    print(f"  พลังงาน (Energy)    : {pet.energy} / 100")
    print(f"  ความสุข (Happiness) : {pet.happiness} / 100")
    print(f"  คะแนนความดื้อ       : {pet.stubbornness_score} / 100")
    print("-" * 45)
    print("1. ให้อาหาร")
    print("2. เล่นกับแมว")
    print("3. ให้แมวนอนพักผ่อน")
    print("4. บันทึกเกมและกลับสู่เมนูหลัก")
    print("=" * 45)


def start_game_loop(pet):
    """ลูปหลักสำหรับการดูแลและเล่นกับน้องแมว"""
    while True:
        render_status(pet)
        choice = input("กรุณาเลือกคำสั่ง (1-4): ").strip()

        if choice == "1":
            pet.feed()
            print(f"\n[+] ให้อาหาร {pet.name} เรียบร้อย! ความหิวเพิ่มขึ้น")
        elif choice == "2":
            pet.play()
            print(f"\n[+] เล่นกับ {pet.name} สนุกจัง! ความสุขเพิ่มขึ้น แต่พลังงานลดลง")
        elif choice == "3":
            pet.rest()
            print(f"\n[+] {pet.name} กำลังนอนหลับปุ๋ย... พลังงานฟื้นฟู")
        elif choice == "4":
            save_game(pet)
            print("\n[!] บันทึกเกมเรียบร้อยแล้ว กำลังกลับสู่เมนูหลัก...")
            time.sleep(1)
            break
        else:
            print("\n[X] กรุณาเลือกตัวเลข 1 ถึง 4 เท่านั้น")
            time.sleep(1)
            continue

        save_game(pet)
        time.sleep(1.2)
