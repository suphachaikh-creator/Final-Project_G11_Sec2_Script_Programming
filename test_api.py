
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
fish_api.py
===========

ดึงข้อมูลปลาโดยอัตโนมัติจาก World Register of Marine Species (WoRMS)
ผ่าน REST API

คุณสมบัติ:
- ไม่ต้องรับ Input จากผู้ใช้
- แบ่งข้อมูลตามแหล่งน้ำ
    1. น้ำจืด (Freshwater)
    2. น้ำเค็ม (Marine)
    3. น้ำกร่อย (Brackish)
- แสดงข้อมูลสูงสุด 10 รายการต่อแหล่งน้ำ
- กรองเฉพาะกลุ่มปลา
- ป้องกันข้อมูลซ้ำด้วย AphiaID
- รองรับค่า habitat ที่เป็น 1/0 และ True/False
- จัดการ API Error และ Timeout
"""

import json
import urllib.error
import urllib.parse
import urllib.request


# ============================================================
# CONFIGURATION
# ============================================================

BASE_URL = "https://www.marinespecies.org/rest"

MAX_RESULTS_PER_HABITAT = 10

# คำค้นที่ใช้กับ WoRMS
# ใช้คำที่มีความหมายเกี่ยวกับปลาแทนการใช้ตัวอักษรเดี่ยว
SEARCH_QUERIES = [
    "fish",
    "shark",
    "ray",
    "eel",
    "salmon",
    "tuna",
    "goby",
    "carp",
    "catfish",
    "perch",
]


# ============================================================
# FISH TAXONOMIC GROUPS
# ============================================================

FISH_CLASSES = {
    "Actinopterygii",
    "Actinopteri",
    "Elasmobranchii",
    "Holocephali",
    "Myxini",
    "Petromyzonti",
    "Cephalaspidomorphi",
    "Chondrichthyes",
    "Cladistii",
    "Sarcopterygii",
    "Coelacanthi",
    "Dipneusti",
    "Teleostei",
    "Chondrostei",
}


# ============================================================
# HABITAT CONFIGURATION
# ============================================================

HABITAT_FIELD_MAP = {
    "freshwater": "isFreshwater",
    "marine": "isMarine",
    "brackish": "isBrackish",
}


HABITAT_THAI_NAME = {
    "freshwater": "น้ำจืด (Freshwater)",
    "marine": "น้ำเค็ม (Marine)",
    "brackish": "น้ำกร่อย (Brackish)",
}


# ============================================================
# HTTP / API
# ============================================================

def _http_get_json(url):
    """
    เรียก WoRMS REST API และคืนค่า JSON
    """

    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "fish-api-script/1.0",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read().decode("utf-8")

            if not raw.strip():
                return []

            return json.loads(raw)

    except urllib.error.HTTPError as error:

        if error.code in (204, 404):
            return []

        raise RuntimeError(
            f"เรียก WoRMS API ไม่สำเร็จ "
            f"(HTTP {error.code})"
        ) from error

    except urllib.error.URLError as error:

        raise RuntimeError(
            f"เชื่อมต่อ WoRMS API ไม่ได้: {error.reason}"
        ) from error

    except TimeoutError as error:

        raise RuntimeError(
            "WoRMS API ตอบกลับช้าเกินไป (timeout)"
        ) from error

    except json.JSONDecodeError as error:

        raise RuntimeError(
            "ข้อมูลที่ได้รับจาก WoRMS API ไม่ใช่ JSON ที่ถูกต้อง"
        ) from error


# ============================================================
# VALUE NORMALIZATION
# ============================================================

def is_true_value(value):
    """
    ตรวจสอบค่า True / 1 / '1' / 'true'
    """

    if value is True:
        return True

    if isinstance(value, int):
        return value == 1

    if isinstance(value, str):
        return value.strip().lower() in {
            "1",
            "true",
            "yes",
            "y",
        }

    return False


# ============================================================
# HABITAT
# ============================================================

def record_matches_habitat(record, habitat):
    """
    ตรวจสอบว่าข้อมูลปลาอยู่ในแหล่งน้ำที่ต้องการหรือไม่
    """

    field = HABITAT_FIELD_MAP.get(habitat)

    if not field:
        return False

    return is_true_value(record.get(field))


def get_habitat_labels(record):
    """
    แปลงข้อมูล habitat จาก API เป็นข้อความภาษาไทย
    """

    labels = []

    if is_true_value(record.get("isMarine")):
        labels.append("น้ำเค็ม (Marine)")

    if is_true_value(record.get("isFreshwater")):
        labels.append("น้ำจืด (Freshwater)")

    if is_true_value(record.get("isBrackish")):
        labels.append("น้ำกร่อย (Brackish)")

    if not labels:
        labels.append(
            "ไม่มีข้อมูลระบุแหล่งที่อยู่ในฐานข้อมูล"
        )

    return labels


# ============================================================
# SEARCH
# ============================================================

def search_by_name(query):
    """
    ค้นหาข้อมูลจากชื่อสิ่งมีชีวิต
    """

    encoded_query = urllib.parse.quote(
        query,
        safe=""
    )

    url = (
        f"{BASE_URL}/AphiaRecordsByName/"
        f"{encoded_query}?like=true&marine_only=false"
    )

    result = _http_get_json(url)

    return result if isinstance(result, list) else []


def search_by_vernacular(query):
    """
    ค้นหาข้อมูลจากชื่อสามัญ
    """

    encoded_query = urllib.parse.quote(
        query,
        safe=""
    )

    url = (
        f"{BASE_URL}/AphiaRecordsByVernacular/"
        f"{encoded_query}?like=true"
    )

    result = _http_get_json(url)

    return result if isinstance(result, list) else []


# ============================================================
# FISH FILTER
# ============================================================

def is_fish(record):
    """
    ตรวจสอบว่าข้อมูลเป็นปลา
    """

    record_class = record.get("class")

    if not record_class:
        return False

    return str(record_class).strip() in FISH_CLASSES


# ============================================================
# SEARCH FISH
# ============================================================

def search_fish(query, habitat):
    """
    ค้นหาปลาตามคำค้นและแหล่งน้ำ
    """

    found = {}

    # --------------------------------------------------------
    # Search by scientific/common name
    # --------------------------------------------------------

    try:
        name_records = search_by_name(query)

        for record in name_records:

            aphia_id = record.get("AphiaID")

            if aphia_id is not None:
                found[aphia_id] = record

    except RuntimeError as error:

        print(
            f"⚠️ ค้นหาจากชื่อไม่สำเร็จ [{query}]: {error}"
        )

    # --------------------------------------------------------
    # Search by vernacular name
    # --------------------------------------------------------

    try:
        vernacular_records = search_by_vernacular(query)

        for record in vernacular_records:

            aphia_id = record.get("AphiaID")

            if aphia_id is not None:
                found.setdefault(
                    aphia_id,
                    record
                )

    except RuntimeError as error:

        print(
            f"⚠️ ค้นหาจากชื่อสามัญไม่สำเร็จ "
            f"[{query}]: {error}"
        )

    # --------------------------------------------------------
    # Filter fish
    # --------------------------------------------------------

    records = [
        record
        for record in found.values()
        if is_fish(record)
    ]

    # --------------------------------------------------------
    # Filter habitat
    # --------------------------------------------------------

    records = [
        record
        for record in records
        if record_matches_habitat(
            record,
            habitat
        )
    ]

    return records


# ============================================================
# VALIDATION
# ============================================================

def is_valid_record(record):
    """
    ตรวจสอบข้อมูลขั้นต่ำก่อนนำมาแสดง
    """

    return bool(
        record.get("AphiaID")
        and record.get("scientificname")
    )


# ============================================================
# COLLECT DATA
# ============================================================

def collect_fish_by_habitat(habitat):
    """
    รวบรวมปลาในแต่ละแหล่งน้ำ
    """

    collected = {}

    for query in SEARCH_QUERIES:

        if len(collected) >= MAX_RESULTS_PER_HABITAT:
            break

        records = search_fish(
            query,
            habitat
        )

        for record in records:

            aphia_id = record.get("AphiaID")

            if not aphia_id:
                continue

            if not is_valid_record(record):
                continue

            if aphia_id not in collected:

                collected[aphia_id] = record

            if len(collected) >= MAX_RESULTS_PER_HABITAT:
                break

    return list(collected.values())[
        :MAX_RESULTS_PER_HABITAT
    ]


# ============================================================
# DISPLAY
# ============================================================

def print_records(records):
    """
    แสดงข้อมูลปลา
    """

    for index, record in enumerate(
        records,
        start=1
    ):

        habitats = get_habitat_labels(
            record
        )

        print()
        print("-" * 70)

        print(
            f"รายการที่       : {index}"
        )

        print(
            f"ชื่อวิทยาศาสตร์ : "
            f"{record.get('scientificname', '-')}"
        )

        print(
            f"ผู้ตั้งชื่อ      : "
            f"{record.get('authority', '-')}"
        )

        print(
            f"AphiaID         : "
            f"{record.get('AphiaID', '-')}"
        )

        print(
            f"อันดับ (Order)  : "
            f"{record.get('order', '-')}"
        )

        print(
            f"วงศ์ (Family)   : "
            f"{record.get('family', '-')}"
        )

        print(
            f"ชั้น (Class)    : "
            f"{record.get('class', '-')}"
        )

        print(
            f"สถานะ           : "
            f"{record.get('status', '-')}"
        )

        print(
            f"แหล่งที่พบ      : "
            f"{', '.join(habitats)}"
        )

        print(
            f"อ้างอิง         : "
            f"{record.get('url', '-')}"
        )

    print()
    print("-" * 70)


# ============================================================
# MAIN
# ============================================================

def main():

    target_habitats = [
        "freshwater",
        "marine",
        "brackish",
    ]

    print()
    print("=" * 70)
    print(
        "🐟 ระบบดึงข้อมูลปลา WoRMS API"
    )
    print(
        "ดึงข้อมูลตามแหล่งน้ำ "
        "แหล่งน้ำละไม่เกิน 10 รายการ"
    )
    print("=" * 70)

    total_records = 0

    for habitat in target_habitats:

        print()
        print("=" * 70)

        print(
            f"📌 แหล่งน้ำ: "
            f"{HABITAT_THAI_NAME[habitat]}"
        )

        print("=" * 70)

        try:

            records = collect_fish_by_habitat(
                habitat
            )

        except Exception as error:

            print(
                f"❌ เกิดข้อผิดพลาด: {error}"
            )

            continue

        if not records:

            print(
                "ไม่พบข้อมูลปลา "
                "สำหรับแหล่งน้ำนี้"
            )

            continue

        print_records(records)

        print(
            f"✅ พบข้อมูลทั้งหมด: "
            f"{len(records)} รายการ"
        )

        total_records += len(records)

    print()
    print("=" * 70)

    print(
        f"🐟 จำนวนข้อมูลทั้งหมด: "
        f"{total_records} รายการ"
    )

    print("=" * 70)


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
