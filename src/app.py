import sys
import os
import time

# เพิ่มโฟลเดอร์ src เข้า path เพื่อให้เรียกใช้งานไฟล์ภายในโฟลเดอร์เดียวกันได้ราบรื่น
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

os.environ["PYTHONIOENCODING"] = "utf-8"
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from app_functions import load_game, save_game, fetch_new_pets
from pet import Pet
from game import start_game_loop

def main_menu():
    while True:
        print("\n" + "="*45)
        print("         🐱 VIRTUAL PET APP - เมนูหลัก 🐱")
        print("="*45)
        print("1. เล่นต่อ (โหลดจากเซฟล่าสุด)")
        print("2. เริ่มใหม่ (ดึงข้อมูลสายพันธุ์จาก API)")
        print("3. โหลด (ตรวจสอบและดึงข้อมูลจาก data/pet_state.json)")
        print("4. ออกจากโปรแกรม")
        print("="*45)
        
        choice = input("กรุณาเลือกเมนู (1-4): ").strip()
        
        if choice == "1":
            pet = load_game()
            if pet is None:
                print("\n[!] ไม่พบเซฟเกมล่าสุด! กรุณาเลือก 'เริ่มใหม่' หรือ 'โหลด' ก่อน")
                time.sleep(1.5)
            else:
                print(f"\n[!] ยินดีต้อนรับกลับมา! กำลังโหลดเซฟของ {pet.name}...")
                time.sleep(1)
                start_game_loop(pet)
                
        elif choice == "2":
            print("\nกำลังเชื่อมต่อ API เพื่อเลือกสายพันธุ์แมว...")
            cats = fetch_new_pets()
            if not cats:
                print("\n[X] ไม่สามารถดึงข้อมูลจาก API ได้ กรุณาตรวจสอบอินเทอร์เน็ตหรือ API Key ใน src/key.py")
                time.sleep(1.5)
                continue
                
            print("\n" + "="*15 + " เลือกสายพันธุ์แมวของคุณ " + "="*15)
            for idx, cat in enumerate(cats, start=1):
                print(f"{idx}. สายพันธุ์: {cat.get('breed')} ({cat.get('country')})")
                print(f"   นิสัย: {cat.get('temperament')}")
                print(f"   คะแนนความดื้อ: {cat.get('stubbornness_score')} / 100")
                print(f"   รายละเอียด: {cat.get('description')}")
                print("-" * 45)
                
            sub_choice = input(f"เลือกหมายเลขสายพันธุ์ (1-{len(cats)}): ").strip()
            if sub_choice.isdigit() and 1 <= int(sub_choice) <= len(cats):
                selected_cat = cats[int(sub_choice) - 1]
                pet_name = input("ตั้งชื่อให้น้องแมวของคุณ: ").strip()
                if not pet_name:
                    pet_name = "น้องเหมียว"
                    
                pet = Pet(
                    name=pet_name,
                    breed=selected_cat.get("breed"),
                    country=selected_cat.get("country"),
                    temperament=selected_cat.get("temperament"),
                    stubbornness_score=selected_cat.get("stubbornness_score", 50),
                    description=selected_cat.get("description")
                )
                save_game(pet)
                print(f"\n[!] สร้างน้องแมว '{pet.name}' สำเร็จ! เริ่มต้นเลี้ยงกันเลย")
                time.sleep(1.5)
                start_game_loop(pet)
            else:
                print("\n[X] ตัวเลือกไม่ถูกต้อง")
                time.sleep(1)
                
        elif choice == "3":
            pet = load_game()
            if pet is None:
                print("\n[!] ไม่พบไฟล์ข้อมูลเซฟใน data/pet_state.json")
                time.sleep(1.5)
            else:
                print(f"\n[!] โหลดข้อมูลของ {pet.name} จาก data/pet_state.json สำเร็จ!")
                time.sleep(1)
                start_game_loop(pet)
                
        elif choice == "4":
            print("\nขอบคุณที่เล่น Virtual Pet App! ไว้พบกันใหม่...")
            break
        else:
            print("\n[X] กรุณาเลือกตัวเลข 1 ถึง 4 เท่านั้น")
            time.sleep(1)

if __name__ == "__main__":
    main_menu()