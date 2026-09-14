"""ข้อมูลจำลองสำหรับ Sprint 1 (in-memory mock)

Sprint 1 เป็นสปรินต์ Front-End จึงยังไม่เรียก API จริงและไม่อ่าน/เขียนไฟล์จริง
ข้อมูลชุดนี้ใช้แทนผลลัพธ์ที่ Sprint 2 จะดึงมาจาก API
"""

MOCK_BREEDS = [
    {
        "breed": "Siamese",
        "country": "ไทย",
        "temperament": "ฉลาด ขี้อ้อน ชอบส่งเสียงคุยกับเจ้าของ",
        "stubbornness_score": 45,
        "description": "แมวไทยโบราณ แต้มสีเข้ม 9 จุด ดวงตาสีฟ้าสดใส",
    },
    {
        "breed": "Persian",
        "country": "อิหร่าน",
        "temperament": "ใจเย็น เรียบร้อย ชอบนอนอยู่กับที่",
        "stubbornness_score": 60,
        "description": "ขนยาวฟูหนา หน้าแบน นิสัยสุขุมไม่ค่อยซน",
    },
    {
        "breed": "Maine Coon",
        "country": "สหรัฐอเมริกา",
        "temperament": "ตัวใหญ่แต่ใจดี ขี้เล่น เข้ากับคนง่าย",
        "stubbornness_score": 30,
        "description": "แมวบ้านขนาดใหญ่ที่สุดสายพันธุ์หนึ่ง ขนยาวหางเป็นพวง",
    },
]

DEFAULT_STATS = {
    "hunger": 50,
    "energy": 50,
    "happiness": 50,
}


def build_mock_pet(name, age, breed):
    """ประกอบข้อมูลน้องแมวเก็บไว้ใน memory (ยังไม่บันทึกลงไฟล์ - รอ Sprint 2)"""
    pet = {
        "name": name,
        "age": age,
        "breed": breed["breed"],
        "country": breed["country"],
        "temperament": breed["temperament"],
        "stubbornness_score": breed["stubbornness_score"],
        "description": breed["description"],
    }
    pet.update(DEFAULT_STATS)
    return pet
