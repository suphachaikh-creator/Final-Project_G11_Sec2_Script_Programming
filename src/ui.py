"""ส่วนแสดงผลทั้งหมด (Sprint 1 — Front-End)

ไฟล์นี้มีเฉพาะ print() ไม่มีการคำนวณตรรกะของเกม
แยกออกจาก cli.py เพื่อให้เปลี่ยนหน้าตาได้โดยไม่ต้องแตะการไหลของเมนู
"""

import os
import sys
import time

LINE = "=" * 46
THIN = "-" * 46

LOCATION_LABELS = {
    "freshwater": "ทะเลสาบน้ำจืด",
    "marine": "ทะเลลึก",
    "brackish": "ปากแม่น้ำน้ำกร่อย",
}


def clear_screen():
    """ล้างหน้าจอให้รองรับทั้ง Windows และระบบตระกูล Unix"""
    os.system("cls" if os.name == "nt" else "clear")


def location_label(location):
    """แปลงรหัสแหล่งน้ำเป็นชื่อภาษาไทย"""
    return LOCATION_LABELS.get(location, location)


def show_header(state):
    """แบนเนอร์และแถบสถานะด้านบนของทุกหน้าจอ"""
    print(LINE)
    print("           FISHING ADVENTURE")
    print(LINE)
    print(f"  เงิน: ${state.money}   ปลาในกระเป๋า: {len(state.inventory)} ตัว")
    print(f"  เลเวลเหยื่อ: {state.bait_level}   เลเวลคันเบ็ด: {state.rod_level}")
    print(THIN)


def show_main_menu():
    """เมนูหลัก 4 ตัวเลือก"""
    print("1. เลือกสถานที่ตกปลา")
    print("2. ร้านค้า (อัปเกรดอุปกรณ์)")
    print("3. คลังสินค้า (ค้นหา กรอง เรียงลำดับ และขาย)")
    print("4. ออกจากเกม (บันทึกอัตโนมัติ)")
    print(LINE)


def show_location_menu():
    """เมนูเลือกสถานที่ตกปลา"""
    print(LINE)
    print("              เลือกสถานที่ตกปลา")
    print(LINE)
    print("1. ทะเลสาบน้ำจืด (ปลาน้ำจืด)")
    print("2. ทะเลลึก (ปลาทะเลไซส์ใหญ่)")
    print("3. ปากแม่น้ำน้ำกร่อย (ปลาสองน้ำ)")
    print("4. กลับสู่เมนูหลัก")
    print(LINE)


def show_shop_menu(state):
    """เมนูร้านค้าพร้อมราคาอัปเกรดปัจจุบัน"""
    print(LINE)
    print("              ร้านค้าอุปกรณ์ตกปลา")
    print(LINE)
    print(f"  เงินที่มี: ${state.money}")
    print(THIN)
    print(f"1. อัปเกรดเหยื่อ   (Lv.{state.bait_level})  ราคา ${state.bait_cost}")
    print(f"2. อัปเกรดคันเบ็ด  (Lv.{state.rod_level})  ราคา ${state.rod_cost}")
    print("3. กลับสู่เมนูหลัก")
    print(LINE)


def show_inventory(fishes, title="คลังสินค้า"):
    """ตารางปลาในกระเป๋า"""
    print(LINE)
    print(f"              {title}")
    print(LINE)

    if not fishes:
        print("  ไม่มีปลาที่ตรงเงื่อนไข")
        print(LINE)
        return

    print(f"  {'#':<3} {'ชนิดปลา':<22} {'แหล่งน้ำ':<14} {'น้ำหนัก':>8} {'ราคา':>7}")
    print(THIN)
    for index, fish in enumerate(fishes, start=1):
        print(
            f"  {index:<3} {fish.name:<22} {location_label(fish.location):<14}"
            f" {fish.weight_kg:>6} กก. {fish.price:>6}$"
        )
    print(LINE)


def show_inventory_menu():
    """เมนูย่อยของหน้าคลังสินค้า"""
    print("1. ค้นหาด้วยชื่อปลา")
    print("2. กรองตามแหล่งน้ำ")
    print("3. เรียงลำดับ (ชื่อ / น้ำหนัก / ราคา)")
    print("4. ขายปลาทั้งหมด")
    print("5. กลับสู่เมนูหลัก")
    print(LINE)


def show_summary(summary):
    """สรุปสถิติการจับปลา"""
    if not summary["count"]:
        return
    heaviest = summary["heaviest"]
    print(f"  จำนวน {summary['count']} ตัว   มูลค่ารวม ${summary['total_price']}")
    print(f"  น้ำหนักเฉลี่ย {summary['average_weight']} กก.   "
          f"ตัวใหญ่ที่สุด {heaviest.name} {heaviest.weight_kg} กก.")
    print(LINE)


def show_casting_animation(rounds=3, delay=0.25):
    """แอนิเมชันรอปลากินเหยื่อ อัปเดตในบรรทัดเดียวด้วย stdout.write"""
    for _ in range(rounds):
        for frame in (".", "..", "...", "...."):
            sys.stdout.write(f"\r  กำลังหย่อนเบ็ดรอปลากินเหยื่อ{frame.ljust(6)}")
            sys.stdout.flush()
            time.sleep(delay)
    sys.stdout.write("\r  ปลากินเบ็ดแล้ว!" + " " * 24 + "\n")
    sys.stdout.flush()


def show_qte_intro(game):
    """อธิบายกติกาของมินิเกมก่อนเริ่มจับเวลา"""
    print(THIN)
    print(f"  ปลากำลังสู้แรง! พิมพ์ให้ครบ {game.total_targets} ตัวอักษร")
    print(f"  เวลาเริ่มต้น {game.time_limit:.1f} วินาที  (พิมพ์ถูกได้เวลาเพิ่ม 1 วินาที)")
    print(f"  โจทย์: {' '.join(target.upper() for target in game.targets)}")
    print(THIN)


def show_catch_result(fish):
    """ผลลัพธ์เมื่อจับปลาได้"""
    print()
    print(f"  จับได้! {fish.name}")
    print(f"  น้ำหนัก {fish.weight_kg} กก.   มูลค่า ${fish.price}")


def show_error(message):
    """ข้อความแจ้งเตือนเมื่ออินพุตไม่ถูกต้อง"""
    print(f"\n  [X] {message}")


def show_info(message):
    """ข้อความแจ้งข่าวทั่วไป"""
    print(f"\n  [!] {message}")


def pause(prompt="(กด Enter เพื่อไปต่อ)"):
    """หยุดรอให้ผู้ใช้อ่านผลลัพธ์ ปิดสตรีมอินพุตแล้วก็ไม่พัง"""
    try:
        input(f"\n  {prompt}")
    except EOFError:
        pass
