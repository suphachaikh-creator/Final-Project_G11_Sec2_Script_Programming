from google import genai
import json

class APIClient:
    @staticmethod
    def get_cats_from_gemini(api_key, limit=5):
        """ใช้ Gemini API Key สร้างข้อมูลสายพันธุ์ นิสัย และคะแนนความดื้อของแมว"""
        if not api_key or "ใส่_" in api_key:
            raise ValueError("กรุณาระบุ Gemini API Key ให้ถูกต้องในไฟล์ src/key.py")
            
        client = genai.Client(api_key=api_key)
        
        prompt = f"""
        ขอข้อมูลสายพันธุ์แมว จำนวน {limit} สายพันธุ์ 
        ขอเป็นรูปแบบ JSON Array ล้วนๆ เท่านั้น โดยแต่ละสมาชิกต้องมีคีย์ดังนี้:
        - "breed": ชื่อสายพันธุ์แมว (ภาษาอังกฤษ)
        - "country": ประเทศถิ่นกำเนิด
        - "temperament": นิสัยหรือพฤติกรรมเด่น (ภาษาไทย)
        - "stubbornness_score": คะแนนความดื้อเป็นตัวเลขตั้งแต่ 1 ถึง 100
        - "description": รายละเอียดเล็กน้อยเกี่ยวกับสายพันธุ์นี้ (ภาษาไทย)
        ไม่ต้องใส่เครื่องหมายครอบโค้ด markdown เช่น ```json หรือข้อความอธิบายใดๆ เพิ่มเติม ให้คืนค่าเป็น JSON string ตรงๆ เลย
        """
        
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=prompt,
        )
        
        text_result = response.text.strip()
        
        if "```json" in text_result:
            text_result = text_result.split("```json")[1].split("```")[0]
        elif "```" in text_result:
            text_result = text_result.split("```")[1].split("```")[0]
            
        return json.loads(text_result.strip())