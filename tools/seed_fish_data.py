"""ดึงข้อมูลชนิดปลาจาก WoRMS และ Open Fisheries มาเก็บเป็นไฟล์ข้อมูลสำรองของเกม

สคริปต์นี้รันแยกต่างหาก ไม่ได้ถูกเรียกตอนเล่นเกม ใช้เมื่อต้องการสร้างหรือรีเฟรช
`data/fish_species.json` ซึ่งเกมจะใช้เมื่อเชื่อมต่อ API ไม่ได้

    python tools/seed_fish_data.py --dry-run           ดูผลลัพธ์โดยไม่เขียนไฟล์
    python tools/seed_fish_data.py --limit 30          เก็บแหล่งน้ำละไม่เกิน 30 ชนิด
    python tools/seed_fish_data.py --limit 0           เก็บเท่าที่ค้นเจอทั้งหมด

แหล่งข้อมูล
    WoRMS            แหล่งที่อยู่ (น้ำจืด / น้ำเค็ม / น้ำกร่อย) และอนุกรมวิธาน
    Open Fisheries   ชื่อสามัญภาษาอังกฤษ จับคู่กับ WoRMS ด้วยชื่อวิทยาศาสตร์
"""

import argparse
import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from src.fish import BRACKISH, FRESHWATER, LOCATIONS, MARINE  # noqa: E402
from src.fish_api import build_entry  # noqa: E402
from src.openfisheries_api import OpenFisheriesAPI  # noqa: E402
from src.worms_api import WormsAPI, matches_habitat  # noqa: E402

DEFAULT_OUTPUT = os.path.join(BASE_DIR, "data", "fish_species.json")

# คำค้นชื่อสามัญ เลือกให้ครอบคลุมทั้งน้ำจืด น้ำเค็ม และน้ำกร่อย
SEARCH_WORDS = [
    "carp", "catfish", "perch", "tilapia", "barb", "goby", "eel", "trout",
    "snapper", "grouper", "mackerel", "herring", "anchovy", "sardine",
    "tuna", "salmon", "cod", "bass", "shark", "ray",
]

THAI_LABEL = {FRESHWATER: "น้ำจืด", MARINE: "น้ำเค็ม", BRACKISH: "น้ำกร่อย"}


def build_parser():
    """กำหนดตัวเลือกของบรรทัดคำสั่ง"""
    parser = argparse.ArgumentParser(
        description="ดึงชนิดปลาจาก WoRMS และเติมชื่อสามัญจาก Open Fisheries")
    parser.add_argument("--limit", type=int, default=30,
                        help="จำนวนชนิดสูงสุดต่อแหล่งน้ำ (0 = ไม่จำกัด) ค่าเริ่มต้น 30")
    parser.add_argument("--output", default=DEFAULT_OUTPUT,
                        help="ไฟล์ปลายทาง ค่าเริ่มต้นคือ data/fish_species.json")
    parser.add_argument("--dry-run", action="store_true",
                        help="แสดงผลลัพธ์โดยไม่เขียนไฟล์")
    return parser


def main(argv=None):
    """จุดเริ่มของสคริปต์ คืนค่า exit code"""
    args = build_parser().parse_args(argv)

    print(f"1) ค้นหาปลาจาก WoRMS ด้วยคำค้น {len(SEARCH_WORDS)} คำ ...")
    worms = WormsAPI(search_words=SEARCH_WORDS)
    records = worms.fetch_fish_records()
    if not records:
        print(f"   ไม่พบข้อมูล — {worms.last_error or 'ค้นไม่เจอ'}")
        return 1
    print(f"   ได้ปลาที่สถานะ accepted {len(records)} ชนิด")

    print("\n2) ดึงชื่อสามัญจาก Open Fisheries ...")
    common_names = OpenFisheriesAPI().fetch_common_names()
    if common_names:
        print(f"   ได้คู่ ชื่อวิทยาศาสตร์ -> ชื่อสามัญ {len(common_names):,} คู่")
    else:
        print("   ดึงไม่สำเร็จ — จะใช้ชื่อวิทยาศาสตร์แทน")

    print("\n3) แยกตามแหล่งน้ำและเติมชื่อสามัญ ...")
    entries = []
    enriched = 0
    for location in LOCATIONS:
        matched = [build_entry(record, location, common_names)
                   for record in records.values()
                   if matches_habitat(record, location)]
        # ให้ชนิดที่มีชื่อสามัญขึ้นก่อน เวลาตัดตาม --limit จะได้ชื่อที่อ่านง่ายเป็นหลัก
        matched.sort(key=lambda item: (item["name"] == item["scientific_name"],
                                       item["name"].lower()))
        if args.limit:
            matched = matched[:args.limit]
        enriched += sum(1 for item in matched
                        if item["name"] != item["scientific_name"])
        entries.extend(matched)
        print(f"   {THAI_LABEL[location]:<10} {len(matched):>3} ชนิด")

    total = len(entries)
    percent = enriched * 100 // total if total else 0
    print(f"\nรวม {total} รายการ  มีชื่อสามัญ {enriched} รายการ ({percent}%)")

    if args.dry_run:
        print("\n[dry-run] ไม่ได้เขียนไฟล์ ตัวอย่าง 5 รายการแรก:")
        for entry in entries[:5]:
            print(f"   {entry['name']:<28} {entry['scientific_name']:<30} "
                  f"({entry['location']})")
        return 0

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(entries, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    print(f"\nเขียนไฟล์เรียบร้อย: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
