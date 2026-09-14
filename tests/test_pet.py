from src.api_client import APIClient

def test_fetch_breeds_and_temperament():
    print("กำลังดึงข้อมูล สายพันธุ์ และ นิสัย ของสัตว์เลี้ยงจาก API จริง...\n")
    
    try:
        data = APIClient.get_cat_breeds_with_temperament(limit=5)
        
        assert data is not None
        assert len(data) >= 5, "ข้อมูลต้องมีอย่างน้อย 5 ตัว"

        for i, item in enumerate(data, start=1):
            print(f"[{i}] สายพันธุ์: {item['breed']}")
            print(f"    • ประเทศถิ่นกำเนิด : {item['country']} ({item['origin']})")
            print(f"    • ลักษณะขน          : {item['coat']}")
            print(f"    • นิสัย/พฤติกรรม    : {item['temperament']}")
            print("-" * 50)

        print("\nทดสอบดึงข้อมูลสายพันธุ์และนิสัยสำเร็จเรียบร้อย!")
        
    except Exception as e:
        print(f"\n[เกิดข้อผิดพลาด]: {e}")

if __name__ == "__main__":
    test_fetch_breeds_and_temperament()