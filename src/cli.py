"""การไหลของเมนูและการรับอินพุต (Sprint 1 — Front-End)

ชั้นนี้ไม่คำนวณกฎของเกมเอง แต่เรียกเมธอดของ GameState, QTEMinigame, FishAPI
และ SaveManager ทำงานให้ หน้าที่ของไฟล์นี้คือ รับคำสั่ง ตรวจอินพุต และสั่งให้ ui วาดผลลัพธ์
"""

import random

from src import ui
from src.fish import BRACKISH, FRESHWATER, MARINE, Fish
from src.fish_api import FishAPI
from src.game_state import GameState, NotEnoughMoneyError
from src.minigame import QTEMinigame
from src.save_manager import SaveManager
from src.validators import (
    is_back_command,
    validate_menu_choice,
    validate_qte_key,
    validate_search_keyword,
)

LOCATION_BY_CHOICE = {1: FRESHWATER, 2: MARINE, 3: BRACKISH}
SORT_BY_CHOICE = {1: "name", 2: "weight", 3: "price"}


class FishingCLI:
    """หน้าจอทั้งหมดของเกมตกปลา"""

    def __init__(self, state=None, api=None, saver=None, rng=None):
        self.saver = saver or SaveManager()
        self.state = state or self.saver.load_or_new()
        self.api = api or FishAPI()
        self.rng = rng or random
        self.running = True

    # ------------------------------------------------------------- อินพุต
    def ask(self, prompt):
        """รับอินพุต ถ้าสตรีมปิดลงถือว่าผู้ใช้สั่งออกจากโปรแกรม"""
        try:
            return input(prompt).strip()
        except EOFError:
            self.running = False
            return ""

    def ask_menu(self, prompt, min_option, max_option):
        """ถามเลือกเมนูซ้ำจนกว่าจะถูกต้อง คืนค่า None เมื่อผู้ใช้สั่งย้อนกลับหรือสตรีมปิด"""
        while self.running:
            raw = self.ask(prompt)
            if not self.running or is_back_command(raw):
                return None
            try:
                return validate_menu_choice(raw, min_option, max_option)
            except ValueError as error:
                ui.show_error(str(error))

        return None

    # --------------------------------------------------------- เมนูหลัก
    def run(self):
        """ลูปหลักของเกม"""
        while self.running:
            ui.clear_screen()
            ui.show_header(self.state)
            ui.show_main_menu()

            choice = self.ask_menu("  เลือกเมนู (1-4): ", 1, 4)
            if choice is None or choice == 4:
                break

            if choice == 1:
                self.location_screen()
            elif choice == 2:
                self.shop_screen()
            elif choice == 3:
                self.inventory_screen()

        self.saver.save(self.state)
        ui.show_info("บันทึกเกมเรียบร้อย ขอบคุณที่เล่นครับ")

    # ------------------------------------------------- หน้าจอเลือกสถานที่
    def location_screen(self):
        """เลือกแหล่งน้ำก่อนออกไปตกปลา"""
        while self.running:
            ui.clear_screen()
            ui.show_header(self.state)
            ui.show_location_menu()

            choice = self.ask_menu("  เลือกสถานที่ (1-4): ", 1, 4)
            if choice is None or choice == 4:
                return
            self.fishing_screen(LOCATION_BY_CHOICE[choice])

    # ------------------------------------------------------ หน้าจอตกปลา
    def fishing_screen(self, location):
        """หย่อนเบ็ด เล่นมินิเกม แล้วเก็บปลาที่จับได้"""
        while self.running:
            ui.clear_screen()
            ui.show_header(self.state)
            print(f"  สถานที่: {ui.location_label(location)}")
            print(ui.THIN)
            print("  กด Enter เพื่อหย่อนเบ็ด  หรือพิมพ์ b เพื่อกลับ")

            action = self.ask("  > ")
            if not self.running or is_back_command(action):
                return

            ui.show_casting_animation()
            if self.play_minigame():
                self.collect_fish(location)
            else:
                ui.show_error("ปลาสะบัดหลุดหนีไปได้")

            ui.pause("(กด Enter เพื่อตกปลาต่อ)")

    def play_minigame(self):
        """เล่นมินิเกม QTE คืนค่า True เมื่อผู้เล่นทำสำเร็จ"""
        game = QTEMinigame(rod_level=self.state.rod_level, rng=self.rng)
        ui.show_qte_intro(game)
        game.start()

        while not game.is_complete:
            if game.is_timed_out():
                ui.show_error("หมดเวลา ปลาหลุดไปแล้ว")
                return False

            target = game.current_target
            raw = self.ask(
                f"  [{game.time_left()}s] พิมพ์ '{target.upper()}' "
                f"({game.hit_count + 1}/{game.total_targets}): "
            )
            if not self.running:
                return False

            try:
                validate_qte_key(raw, target)
            except ValueError as error:
                ui.show_error(str(error))
                continue

            if game.submit(raw):
                if not game.is_complete:
                    print(f"  ถูกต้อง! เหลืออีก {game.total_targets - game.hit_count} ตัว")
            else:
                ui.show_error("พิมพ์ผิดตัว")

        return True

    def collect_fish(self, location):
        """ขอชนิดปลาจาก API คำนวณน้ำหนักราคา แล้วเก็บเข้ากระเป๋าและเซฟ"""
        species = self.api.random_species(location, rng=self.rng)
        fish = Fish.catch(species.get("name", "ปลาปริศนา"), location,
                          self.state.bait_level, rng=self.rng)

        self.state.add_fish(fish)
        self.saver.save(self.state)

        ui.show_catch_result(fish)
        if species.get("description"):
            print(f"  เกร็ดความรู้: {species['description']}")
        if self.api.using_fallback:
            ui.show_info("ขณะนี้ใช้ฐานข้อมูลปลาสำรองในเครื่อง (เชื่อมต่อ WoRMS ไม่ได้)")

    # ------------------------------------------------------ หน้าจอร้านค้า
    def shop_screen(self):
        """อัปเกรดเหยื่อและคันเบ็ด"""
        while self.running:
            ui.clear_screen()
            ui.show_header(self.state)
            ui.show_shop_menu(self.state)

            choice = self.ask_menu("  เลือกรายการ (1-3): ", 1, 3)
            if choice is None or choice == 3:
                return

            try:
                if choice == 1:
                    level = self.state.upgrade_bait()
                    ui.show_info(f"อัปเกรดเหยื่อสำเร็จ เป็นเลเวล {level}")
                else:
                    level = self.state.upgrade_rod()
                    ui.show_info(f"อัปเกรดคันเบ็ดสำเร็จ เป็นเลเวล {level}")
                self.saver.save(self.state)
            except NotEnoughMoneyError as error:
                ui.show_error(str(error))

            ui.pause()

    # ---------------------------------------------------- หน้าจอคลังสินค้า
    def inventory_screen(self):
        """ค้นหา กรอง เรียงลำดับ และขายปลา"""
        while self.running:
            ui.clear_screen()
            ui.show_header(self.state)
            ui.show_inventory(self.state.inventory)
            ui.show_summary(self.state.summary())
            ui.show_inventory_menu()

            choice = self.ask_menu("  เลือกเมนู (1-5): ", 1, 5)
            if choice is None or choice == 5:
                return

            if choice == 1:
                self.search_screen()
            elif choice == 2:
                self.filter_screen()
            elif choice == 3:
                self.sort_screen()
            elif choice == 4:
                self.sell_all()

    def search_screen(self):
        """ค้นปลาในกระเป๋าด้วยชื่อ"""
        raw = self.ask("  พิมพ์ชื่อปลาที่ต้องการค้น: ")
        if not self.running:
            return
        try:
            keyword = validate_search_keyword(raw)
        except ValueError as error:
            ui.show_error(str(error))
            ui.pause()
            return

        found = self.state.search_inventory(keyword)
        ui.show_inventory(found, title=f"ผลการค้นหา '{keyword}'")
        ui.pause()

    def filter_screen(self):
        """กรองปลาตามแหล่งน้ำ"""
        ui.show_location_menu()
        choice = self.ask_menu("  กรองจากแหล่งน้ำใด (1-4): ", 1, 4)
        if choice is None or choice == 4:
            return

        location = LOCATION_BY_CHOICE[choice]
        found = self.state.filter_inventory(location)
        ui.show_inventory(found, title=f"ปลาจาก{ui.location_label(location)}")
        ui.pause()

    def sort_screen(self):
        """เรียงลำดับปลาในกระเป๋า"""
        print("1. เรียงตามชื่อ")
        print("2. เรียงตามน้ำหนัก (มากไปน้อย)")
        print("3. เรียงตามราคา (มากไปน้อย)")
        choice = self.ask_menu("  เลือกวิธีเรียง (1-3): ", 1, 3)
        if choice is None:
            return

        key = SORT_BY_CHOICE[choice]
        ordered = self.state.sort_inventory(key=key, descending=key != "name")
        ui.show_inventory(ordered, title=f"เรียงตาม {key}")
        ui.pause()

    def sell_all(self):
        """ขายปลาทั้งกระเป๋า"""
        if not self.state.inventory:
            ui.show_error("กระเป๋าว่างเปล่า ออกไปตกปลาก่อน")
            ui.pause()
            return

        total = self.state.sell_all()
        self.saver.save(self.state)
        ui.show_info(f"ขายปลาทั้งหมดเรียบร้อย ได้รับเงิน ${total}")
        ui.pause()


def build_default_state():
    """สร้างสถานะเริ่มต้นสำหรับกรณีที่ยังไม่มีไฟล์เซฟ"""
    return GameState()
