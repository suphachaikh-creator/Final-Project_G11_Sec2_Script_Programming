import json
import os
import random
import string
import sys
import time
from api import FishAPI

SAVE_FILE = "save_game.json"


class FishingGame:

  def __init__(self):
    self.api = FishAPI()
    self.money = 100
    self.inventory = []
    self.bait_level = 1
    self.rod_level = 1
    self.load_game()

  def clear_screen(self):
    os.system("cls" if os.name == "nt" else "clear")

  def save_game(self):
    data = {
        "money": self.money,
        "inventory": self.inventory,
        "bait_level": self.bait_level,
        "rod_level": self.rod_level,
    }
    try:
      with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception:
      pass

  def load_game(self):
    if os.path.exists(SAVE_FILE):
      try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
          data = json.load(f)
          self.money = data.get("money", 100)
          self.inventory = data.get("inventory", [])
          self.bait_level = data.get("bait_level", 1)
          self.rod_level = data.get("rod_level", 1)
          print("💾 โหลดเซฟเกมสำเร็จ!")
          time.sleep(0.8)
      except Exception:
        pass

  def start(self):
    while True:
      self.clear_screen()
      print("==================================")
      print("        🎣 FISHING ADVENTURE 🎣     ")
      print("==================================")
      print(f"💰 เงิน: ${self.money} | 🎒 ปลาในกระเป๋า: {len(self.inventory)} ตัว")
      print(
          f"⚙️ เลเวลเหยื่อ: {self.bait_level} | เลเวลคันเบ็ด: {self.rod_level}"
      )
      print("----------------------------------")
      print("1. เลือกสถานที่ตกปลา")
      print("2. ร้านค้า (อัปเกรดอุปกรณ์)")
      print("3. ดูรายชื่อปลาทั้งหมดและขาย")
      print("4. ออกจากเกม (บันทึกอัตโนมัติ)")
      print("==================================")

      choice = input("เลือกเมนู (1-4): ")

      if choice == "1":
        self.select_location_menu()
      elif choice == "2":
        self.shop_menu()
      elif choice == "3":
        self.inventory_menu()
      elif choice == "4":
        self.save_game()
        print("💾 บันทึกเกมเรียบร้อย ขอบคุณที่เล่นเกมครับ!")
        sys.exit()
      else:
        input("❌ กรุณาเลือกตัวเลข 1-4 เท่านั้น (กด Enter)")

  def select_location_menu(self):
    while True:
      self.clear_screen()
      print("=== 🗺️ เลือกสถานที่ตกปลา ===")
      print("1. ทะเลสาบน้ำจืด (ปลาน้ำจืด)")
      print("2. ทะเลลึก (ปลาทะเลไซส์ใหญ่)")
      print("3. กลับสู่เมนูหลัก")

      loc = input("เลือกสถานที่ (1-3): ")
      if loc == "1":
        self.fishing_loop("น้ำจืด")
      elif loc == "2":
        self.fishing_loop("ทะเลลึก")
      elif loc == "3":
        break

  def fishing_loop(self, location_name):
    """ลูปตกปลา ตกได้เรื่อยๆ จนกว่าจะกด 'b' เพื่อกลับ"""
    while True:
      self.clear_screen()
      print(f"=== สถานที่: {location_name} ===")
      print("กด [Enter] เพื่อหย่อนเบ็ด (หรือพิมพ์ 'b' เพื่อกลับหน้าเลือกสถานที่)")

      action = input()
      if action.lower() == "b":
        break

      # แอนิเมชันรอปลากินเหยื่อ (ไม่มีตัวเลขถอยหลัง)
      anim_frames = [".", "..", "...", "...."]
      wait_rounds = random.randint(3, 6)
      for _ in range(wait_rounds):
        for frame in anim_frames:
          sys.stdout.write(
              f"\r🎣 กำลังหย่อนเบ็ดรอปลากินเหยื่อ{frame.ljust(5)}"
          )
          sys.stdout.flush()
          time.sleep(0.3)

      print("\r✨ ตู้ม! ปลากินเบ็ดแล้ว!                           ")
      time.sleep(0.5)

      # มินิเกม QTE
      success = self.minigame_qte()

      if success:
        raw_fish = self.api.get_fish_by_location(location_name)
        fish_name = raw_fish["name"]

        base_weight = random.uniform(0.5, 5.0)
        multiplier = 1 + (self.bait_level * 0.5)
        weight = round(base_weight * multiplier, 2)
        price = int(weight * 15 * self.bait_level)

        print(f"\n🎉 เยี่ยมมาก! คุณตกปลาได้สำเร็จ!")
        print(
            f"🐟 ชนิด: {fish_name} | ⚖️ น้ำหนัก: {weight} กก. | 💵 มูลค่า:"
            f" ${price}"
        )

        self.inventory.append(
            {"name": fish_name, "weight": weight, "price": price}
        )
        self.save_game()
      else:
        print("\n❌ น่าเสียดาย! ปลาสะบัดหลุดหนีไปได้...")

      input("\n(กด Enter เพื่อตกปลาต่อ...)")

  def minigame_qte(self):
    """มินิเกมสุ่มจำนวนตัวอักษร พิมพ์ถูกได้เวลาเพิ่ม"""
    target_length = random.randint(6, 12)
    target_chars = [
        random.choice(string.ascii_lowercase) for _ in range(target_length)
    ]
    time_limit = max(4.0, 6.0 + (self.rod_level * 0.5))

    print(
        f"\n⚠️ ปลากำลังสู้แรง! จงพิมพ์ตัวอักษรให้ทัน ({target_length} ตัว)!"
    )
    print(f"⏱️ เวลาเริ่มต้น: {time_limit:.1f} วิ (พิมพ์ถูกได้เวลาเพิ่ม +1 วิ)")
    print(f"🎯 เป้าหมาย: {' '.join(target_chars)}")
    print("-" * 35)

    start_time = time.time()
    correct_count = 0

    while correct_count < target_length:
      elapsed = time.time() - start_time
      if elapsed > time_limit:
        print("\n⏰ หมดเวลา! ปลาหลุดไปแล้ว")
        return False

      remaining_time = round(time_limit - elapsed, 1)
      current_target = target_chars[correct_count]

      user_input = input(
          f"[{remaining_time}s] พิมพ์ตัวอักษร '{current_target.upper()}'"
          f" ({correct_count+1}/{target_length}): "
      ).lower()

      if user_input == current_target:
        correct_count += 1
        start_time += 1.0  # เพิ่มเวลาเมื่อพิมพ์ถูก
        if correct_count < target_length:
          print(
              f"✅ ถูกต้อง! (+1 วิ) เหลืออีก {target_length - correct_count} ตัว"
          )
      else:
        print("❌ พิมพ์ผิดตัว!")

    return True

  def shop_menu(self):
    while True:
      self.clear_screen()
      print("=== 🏪 ร้านค้าอุปกรณ์ตกปลา ===")
      print(f"💰 เงินที่มี: ${self.money}")
      print(
          f"1. ซื้อเหยื่อเพิ่มขนาดปลา (เลเวล: {self.bait_level}) - ราคา:"
          f" ${self.bait_level * 50}"
      )
      print(
          f"2. ซื้อคันเบ็ดเพิ่มเวลาสู้ปลา (เลเวล: {self.rod_level}) - ราคา:"
          f" ${self.rod_level * 50}"
      )
      print("3. กลับสู่เมนูหลัก")

      choice = input("เลือกรายการ (1-3): ")

      if choice == "1":
        cost = self.bait_level * 50
        if self.money >= cost:
          self.money -= cost
          self.bait_level += 1
          self.save_game()
          print(f"🎉 อัปเกรดเหยื่อสำเร็จ! เป็นเลเวล {self.bait_level}")
        else:
          print("❌ เงินไม่พอ!")
        input("(กด Enter)")

      elif choice == "2":
        cost = self.rod_level * 50
        if self.money >= cost:
          self.money -= cost
          self.rod_level += 1
          self.save_game()
          print(f"🎉 อัปเกรดคันเบ็ดสำเร็จ! เป็นเลเวล {self.rod_level}")
        else:
          print("❌ เงินไม่พอ!")
        input("(กด Enter)")

      elif choice == "3":
        break

  def inventory_menu(self):
    while True:
      self.clear_screen()
      print("=== 🎒 กระเป๋าปลาและตลาดขายปลา ===")
      if not self.inventory:
        print("กระเป๋าว่างเปล่า ออกไปตกปลาก่อนสิ!")
      else:
        for idx, fish in enumerate(self.inventory, 1):
          print(
              f"{idx}. {fish['name']} | น้ำหนัก: {fish['weight']} กก. | ราคา:"
              f" ${fish['price']}"
          )

      print("-" * 40)
      print("1. ขายปลาทั้งหมดในกระเป๋า")
      print("2. กลับสู่เมนูหลัก")

      choice = input("เลือกเมนู (1-2): ")

      if choice == "1" and self.inventory:
        total_price = sum(fish["price"] for fish in self.inventory)
        self.money += total_price
        print(f"💰 ขายปลาทั้งหมดเรียบร้อย ได้รับเงิน ${total_price}!")
        self.inventory.clear()
        self.save_game()
        input("(กด Enter)")
      elif choice == "2":
        break
      else:
        input("(กด Enter)")