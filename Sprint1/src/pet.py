class Pet:
    def __init__(self, name, breed, country, temperament, stubbornness_score, description):
        self.name = name
        self.breed = breed
        self.country = country
        self.temperament = temperament
        self.stubbornness_score = stubbornness_score
        self.description = description
        self.hunger = 50       # 0 (หิวโซ) - 100 (อิ่มท้อง)
        self.energy = 50       # 0 (หมดแรง) - 100 (พลังงานเต็มเปี่ยม)
        self.happiness = 50    # 0 (เศร้า) - 100 (มีความสุข)

    def feed(self):
        """ให้อาหาร เพิ่มความหิวและความสุขเล็กน้อย"""
        self.hunger = min(100, self.hunger + 25)
        self.happiness = min(100, self.happiness + 5)
        
    def play(self):
        """เล่นกับแมว พลังงานและความหิวลดลง แต่ความสุขเพิ่มขึ้น"""
        cost = 10 + (self.stubbornness_score / 10)
        self.energy = max(0, self.energy - cost)
        self.happiness = min(100, self.happiness + 20)
        self.hunger = max(0, self.hunger - 10)

    def rest(self):
        """นอนพักผ่อน ฟื้นฟูพลังงาน"""
        self.energy = min(100, self.energy + 35)
        self.hunger = max(0, self.hunger - 5)

    def to_dict(self):
        """แปลงสถานะเป็น Dictionary เพื่อบันทึกไฟล์ JSON"""
        return {
            "name": self.name,
            "breed": self.breed,
            "country": self.country,
            "temperament": self.temperament,
            "stubbornness_score": self.stubbornness_score,
            "description": self.description,
            "hunger": self.hunger,
            "energy": self.energy,
            "happiness": self.happiness
        }

    @classmethod
    def from_dict(cls, data):
        """สร้าง Object Pet จากข้อมูลในไฟล์เซฟ"""
        pet = cls(
            name=data.get("name", "น้องเหมียว"),
            breed=data.get("breed", "Unknown"),
            country=data.get("country", "Unknown"),
            temperament=data.get("temperament", "-"),
            stubbornness_score=data.get("stubbornness_score", 50),
            description=data.get("description", "-")
        )
        pet.hunger = data.get("hunger", 50)
        pet.energy = data.get("energy", 50)
        pet.happiness = data.get("happiness", 50)
        return pet