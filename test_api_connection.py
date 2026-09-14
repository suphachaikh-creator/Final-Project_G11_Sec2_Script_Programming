import os
import sys
import time
import threading

# ป้องกันปัญหา Windows Console Encoding Error
os.environ["PYTHONIOENCODING"] = "utf-8"

from src.key import GEMINI_API_KEY
from src.api_client import APIClient

def test_fetch_cats_from_gemini():
    print("กำลังเรียกใช้งาน Gemini API เพื่อดึงและวิเคราะห์ข้อมูลแมว...")
    
    is_running = True
    
    def show_timer():
        start_time = time.time()
        while is_running:
            elapsed = int(time.time() - start_time)
            sys.stdout.write(f"\r[Loading] กำลังทำงาน... ผ่านไป {elapsed} วินาที")
            sys.stdout.flush()
            time.sleep(1)

    timer_thread = threading.Thread(target=show_timer)
    timer_thread.start()
    
    try:
        cats_data = APIClient.get_cats_from_gemini(api_key=GEMINI_API_KEY, limit=5)
        
        is_running = False
        timer_thread.join()
        print("\n")
        
        assert cats_data is not None
        assert len(cats_data) >= 5, "ข้อมูลต้องมีอย่างน้อย 5 ตัว"

        for i, item in enumerate(cats_data[:5], start=1):
            print(f"[{i}] สายพันธุ์: {item.get('breed')}")
            print(f"    • ประเทศถิ่นกำเนิด     : {item.get('country')}")
            print(f"    • นิสัย/พฤติกรรม        : {item.get('temperament')}")
            print(f"    • คะแนนความดื้อ (0-100) : {item.get('stubbornness_score')} / 100")
            print(f"    • รายละเอียดเล็กน้อย    : {item.get('description')}")
            print("-" * 60)

        print("\nดึงและวิเคราะห์ข้อมูลจาก Gemini สำเร็จเรียบร้อย!")
        
    except Exception as e:
        is_running = False
        timer_thread.join()
        print("\n")
        print(f"\n[เกิดข้อผิดพลาด]: {e}")

if __name__ == "__main__":
    test_fetch_cats_from_gemini()