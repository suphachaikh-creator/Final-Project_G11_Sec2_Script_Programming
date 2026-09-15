import random
import requests

# ฐานข้อมูลปลาสำรอง แบ่งประเภทแหล่งน้ำชัดเจน (น้ำจืด และ ทะเลลึก)
FALLBACK_FISH = [
    # กลุ่มปลาน้ำจืด (Freshwater)
    {
        "Species Name": "Catfish",
        "Habitat": "Freshwater",
        "Description": "ปลาดุกน้ำจืดตัวอ้วนพี หนวดงาม",
    },
    {
        "Species Name": "Nile Tilapia",
        "Habitat": "Freshwater",
        "Description": "ปลานิลยอดนิยม หาซื้อง่าย",
    },
    {
        "Species Name": "Giant Gourami",
        "Habitat": "Freshwater",
        "Description": "ปลากรอ์ดน้ำจืดขนาดใหญ่",
    },
    {
        "Species Name": "Striped Snakehead",
        "Habitat": "Freshwater",
        "Description": "ปลาช่อนนักล่าแห่งสายน้ำจืด",
    },
    {
        "Species Name": "Common Carp",
        "Habitat": "Freshwater",
        "Description": "ปลาในทองคำ ว่ายน้ำสง่างาม",
    },
    {
        "Species Name": "Black Crappie",
        "Habitat": "Freshwater",
        "Description": "ปลาตัวแบนลายจุดน้ำจืดขนาดเล็ก",
    },
    {
        "Species Name": "Largemouth Bass",
        "Habitat": "Freshwater",
        "Description": "ปลาแบสปากกว้าง ขวัญใจนักตกปลา",
    },
    {
        "Species Name": "Yellow Perch",
        "Habitat": "Freshwater",
        "Description": "ปลาสีเหลืองลายขวางตัวปานกลาง",
    },
    # กลุ่มปลาทะเล / ทะเลลึก (Saltwater)
    {
        "Species Name": "Red Snapper",
        "Habitat": "Saltwater",
        "Description": "ปลากะพงแดงรสชาติดี เนื้อหวาน",
    },
    {
        "Species Name": "Atlantic Salmon",
        "Habitat": "Saltwater",
        "Description": "ปลาแซลมอนยอดฮิต ไขมันดีสูง",
    },
    {
        "Species Name": "Yellowfin Tuna",
        "Habitat": "Saltwater",
        "Description": "ปลาทูน่าครีบเหลืองตัวใหญ่",
    },
    {
        "Species Name": "Halibut",
        "Habitat": "Saltwater",
        "Description": "ปลาแผ่นยักษ์นอนก้นทะเลลึก",
    },
    {
        "Species Name": "Mackerel",
        "Habitat": "Saltwater",
        "Description": "ปลาทูทะเล เนื้อนุ่มมันอร่อย",
    },
    {
        "Species Name": "Pacific Cod",
        "Habitat": "Saltwater",
        "Description": "ปลาคอดแปซิฟิก เนื้อขาวนุ่ม",
    },
    {
        "Species Name": "Mahi Mahi",
        "Habitat": "Saltwater",
        "Description": "ปลาสีสันสวยงาม นักวิ่งเร็วแห่งท้องทะเล",
    },
    {
        "Species Name": "Swordfish",
        "Habitat": "Saltwater",
        "Description": "ปลาอินทรีดาบ ง้าวเหล็กใต้น้ำ",
    },
    {
        "Species Name": "Blue Marlin",
        "Habitat": "Saltwater",
        "Description": "ปลามาร์ลินสีน้ำเงิน ราชาแห่งนักกีฬาตกปลา",
    },
    {
        "Species Name": "Red Drum",
        "Habitat": "Saltwater",
        "Description": "ปลาแดงลายจุด หายากและสู้เบ็ดเก่ง",
    },
]


class FishAPI:

  def __init__(self):
    self.fish_cache = []
    self.load_fish_data()

  def load_fish_data(self):
    """โหลดข้อมูลปลา (เชื่อมต่อ API หรือใช้สำรอง)"""
    print("🎣 กำลังเชื่อมต่อฐานข้อมูลปลา...")
    url = ""
    try:
      response = requests.get(url, timeout=4)
      if response.status_code == 200:
        data = response.json()
        if data:
          # เติม Habitat ให้ API จริงแบบสุ่มถ้าไม่มีระบุ เพื่อให้ระบบแยกน้ำจืด/เค็มได้สมบูรณ์
          for item in data:
            if "Habitat" not in item:
              item["Habitat"] = random.choice(["Freshwater", "Saltwater"])
          self.fish_cache = data
          print(f"✅ โหลดข้อมูลสำเร็จ! ทั้งหมด {len(self.fish_cache)} ชนิด")
          return
    except Exception:
      pass

    # หากดึง API ไม่สำเร็จ ใช้ข้อมูลสำรองชุดใหญ่
    self.fish_cache = FALLBACK_FISH
    print(f"📦 ใช้ฐานข้อมูลปลาสำรอง: {len(self.fish_cache)} ชนิด")

  def get_fish_by_location(self, location_type):
    """กรองและสุ่มปลาตามสถานที่ที่เลือก (น้ำจืด หรือ ทะเลลึก)"""
    target_habitat = "Freshwater" if location_type == "น้ำจืด" else "Saltwater"

    # กรองเฉพาะปลาที่อยู่ในแหล่งน้ำนั้นๆ
    filtered = [
        f
        for f in self.fish_cache
        if f.get("Habitat") == target_habitat
        or f.get("habitat") == target_habitat
    ]

    if not filtered:
      filtered = [f for f in FALLBACK_FISH if f.get("Habitat") == target_habitat]

    if not filtered:
      return {"name": "ปลาปริศนา"}

    fish = random.choice(filtered)
    name = fish.get("Species Name") or fish.get("name", "Unknown Fish")
    return {"name": name}