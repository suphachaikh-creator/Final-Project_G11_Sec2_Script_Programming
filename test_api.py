import random
import requests


def test_gbif_game_data():
  print("🧪 กำลังทดสอบดึงข้อมูลปลาและจำลองสเตตัสสำหรับเกมตกปลา...")
  # ดึงข้อมูลตัวอย่าง 5 รายการจาก GBIF API
  url = "https://api.gbif.org/v1/species/search?q=fish&limit=5"

  try:
    response = requests.get(url, timeout=5)
    print(f"📡 สถานะการเชื่อมต่อ (Status Code): {response.status_code}\n")

    if response.status_code == 200:
      data = response.json()
      results = data.get("results", [])

      print("=" * 50)
      for i, item in enumerate(results, 1):
        # 1. ชื่อปลา (ดึงจาก API)
        name = item.get("canonicalName") or item.get(
            "scientificName", "ปลาปริศนา"
        )

        # 2. ข้อมูลวงศ์จาก API มาช่วยกำหนดกลุ่ม
        family = item.get("family", "ทั่วไป")

        # 3. แหล่งที่พบเจอบ่อย (สุ่มจำลองตามประเภทหรือสภาพแวดล้อม)
        habitats = [
            "น้ำจืด (แม่น้ำ/ทะเลสาบใส)",
            "ทะเลลึก (เขตน้ำเย็น)",
            "แนวปะการังน้ำตื้น",
            "ปากแม่น้ำ (น้ำกร่อย)",
        ]
        habitat = random.choice(habitats)

        # 4. น้ำหนัก (จำลองการสุ่มน้ำหนักเป็นกิโลกรัม)
        weight = round(random.uniform(0.8, 12.5), 2)

        # 5. ราคา (คำนวณจากน้ำหนักคูณเรทราคา)
        price = int(weight * 25)

        print(f"🎣 ปลาตัวที่ {i}:")
        print(f"  • ชื่อ: {name} (วงศ์: {family})")
        print(f"  • แหล่งที่พบเจอบ่อย: {habitat}")
        print(f"  • น้ำหนัก: {weight} กก.")
        print(f"  • ราคาขาย: ${price}")
        print("-" * 50)

      print("\n✨ ทดสอบแสดงข้อมูลสำเร็จ! โครงสร้างข้อมูลพร้อมใช้งานในเกมค่ะ")
    else:
      print(f"⚠️ API ตอบกลับด้วยรหัสผิดพลาด: {response.status_code}")

  except Exception as e:
    print(f"❌ เกิดข้อผิดพลาด: {e}")


if __name__ == "__main__":
  test_gbif_game_data()