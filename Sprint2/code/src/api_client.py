"""เชื่อมต่อ Gemini API เพื่อดึงข้อมูลสายพันธุ์แมว (Sprint 2: Back-End)"""

import json


class APIClient:
    MODEL_NAME = "gemini-3.6-flash"

    @staticmethod
    def build_prompt(limit):
        """สร้าง prompt ที่บังคับให้ผลลัพธ์กลับมาเป็น JSON Array ล้วน"""
        return f"""
        ขอข้อมูลสายพันธุ์แมว จำนวน {limit} สายพันธุ์
        ขอเป็นรูปแบบ JSON Array ล้วนๆ เท่านั้น โดยแต่ละสมาชิกต้องมีคีย์ดังนี้:
        - "breed": ชื่อสายพันธุ์แมว (ภาษาอังกฤษ)
        - "country": ประเทศถิ่นกำเนิด
        - "temperament": นิสัยหรือพฤติกรรมเด่น (ภาษาไทย)
        - "stubbornness_score": คะแนนความดื้อเป็นตัวเลขตั้งแต่ 1 ถึง 100
        - "description": รายละเอียดเล็กน้อยเกี่ยวกับสายพันธุ์นี้ (ภาษาไทย)
        ไม่ต้องใส่เครื่องหมายครอบโค้ด markdown เช่น ```json หรือข้อความอธิบายใดๆ
        ให้คืนค่าเป็น JSON string ตรงๆ เลย
        """

    @staticmethod
    def strip_code_fence(text):
        """ตัดเครื่องหมาย markdown code fence ออกก่อนแปลงเป็น JSON"""
        cleaned = text.strip()

        if "```json" in cleaned:
            cleaned = cleaned.split("```json")[1].split("```")[0]
        elif "```" in cleaned:
            cleaned = cleaned.split("```")[1].split("```")[0]

        return cleaned.strip()

    @staticmethod
    def parse_response(text):
        """แปลงข้อความตอบกลับเป็น list ของ dict"""
        return json.loads(APIClient.strip_code_fence(text))

    @staticmethod
    def get_cats_from_gemini(api_key, limit=5):
        """เรียก Gemini API เพื่อสร้างข้อมูลสายพันธุ์ นิสัย และคะแนนความดื้อของแมว"""
        if not api_key:
            raise ValueError("กรุณาตั้งค่า GEMINI_API_KEY ก่อนใช้งาน (ดู .env.example)")

        try:
            from google import genai
        except ImportError as error:
            raise RuntimeError(
                "ไม่พบไลบรารี google-genai กรุณารัน: pip install -r requirements.txt"
            ) from error

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=APIClient.MODEL_NAME,
            contents=APIClient.build_prompt(limit),
        )

        return APIClient.parse_response(response.text)
