"""ตรวจความพร้อมก่อนปล่อยเวอร์ชัน และดึง release notes จาก CHANGELOG (Final Sprint)

GitHub Actions เรียกสคริปต์นี้ใน `.github/workflows/release.yml` ก่อนสร้าง release
รันเองในเครื่องก็ได้ก่อน push tag

    python tools/release.py check v1.0.1    ตรวจว่า tag · __version__ · CHANGELOG ตรงกัน
    python tools/release.py notes v1.0.1    พิมพ์หัวข้อของเวอร์ชันนั้นใน CHANGELOG

ป้องกันความผิดพลาดที่เกิดง่ายที่สุดตอนปล่อยเวอร์ชัน — ลืมแก้เลขใน `src/__init__.py`
หรือลืมเขียน CHANGELOG ผู้เล่นจะได้เกมที่บอกเวอร์ชันผิด และการแจ้งเตือนอัปเดตจะเพี้ยน
"""

import os
import re
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from src import __version__  # noqa: E402  (ต้องเพิ่ม path ก่อน import)
from src.update_checker import parse_version  # noqa: E402

CHANGELOG = os.path.join(BASE_DIR, "CHANGELOG.md")
HEADING = re.compile(r"^## \[(?P<version>[^\]]+)\]", re.MULTILINE)


def changelog_versions(text):
    """เลขเวอร์ชันทุกหัวข้อใน CHANGELOG เรียงจากบนลงล่าง"""
    return [match.group("version") for match in HEADING.finditer(text)]


def changelog_section(text, version):
    """เนื้อหาของหัวข้อ `## [version]` จนถึงหัวข้อถัดไป คืน None ถ้าไม่มี"""
    matches = list(HEADING.finditer(text))
    for index, match in enumerate(matches):
        if match.group("version") != version:
            continue
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[match.start():end].strip()
        # ตัดเส้นคั่นท้ายหัวข้อออก ไม่ให้ไปโผล่ใน release notes
        return re.sub(r"\n-{3,}\s*$", "", body).strip()
    return None


def problems(tag, code_version, changelog_text):
    """รายการปัญหาที่ทำให้ยังปล่อยเวอร์ชันนี้ไม่ได้ ลิสต์ว่างแปลว่าพร้อม"""
    found = []
    tag_version = parse_version(tag)
    if tag_version is None or not tag.startswith("v"):
        return [f"tag '{tag}' ต้องอยู่ในรูป vMAJOR.MINOR.PATCH เช่น v1.0.1"]

    version = tag[1:]
    if parse_version(code_version) != tag_version:
        found.append(f"src/__init__.py บอก __version__ = '{code_version}' แต่ tag เป็น {tag}")

    versions = changelog_versions(changelog_text)
    if version not in versions:
        found.append(f"CHANGELOG.md ยังไม่มีหัวข้อ ## [{version}]")
    elif versions[0] != version:
        found.append(f"หัวข้อบนสุดของ CHANGELOG.md คือ [{versions[0]}] ไม่ใช่ [{version}]")
    return found


def main(argv):
    if len(argv) != 3 or argv[1] not in ("check", "notes"):
        print(__doc__)
        return 2
    command, tag = argv[1], argv[2]
    with open(CHANGELOG, encoding="utf-8") as handle:
        text = handle.read()

    if command == "check":
        found = problems(tag, __version__, text)
        for item in found:
            print(f"✘ {item}")
        if found:
            return 1
        print(f"✔ พร้อมปล่อย {tag}")
        return 0

    section = changelog_section(text, tag.lstrip("v"))
    if section is None:
        print(f"CHANGELOG.md ไม่มีหัวข้อของ {tag}", file=sys.stderr)
        return 1
    print(section)
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv))
