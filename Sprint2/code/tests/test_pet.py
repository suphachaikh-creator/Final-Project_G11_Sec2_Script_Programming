"""Unit tests ของตรรกะการเลี้ยง (คลาส Pet) - ทำงานแบบออฟไลน์ ไม่เรียก API"""

import pytest

from src.pet import Pet


@pytest.fixture
def pet():
    return Pet(
        name="มิว",
        breed="Siamese",
        country="ไทย",
        temperament="ขี้อ้อน",
        stubbornness_score=50,
        description="แมวไทยโบราณ",
    )


class TestDefaultStats:
    def test_starts_at_fifty(self, pet):
        assert (pet.hunger, pet.energy, pet.happiness) == (50, 50, 50)


class TestFeed:
    def test_increases_hunger_and_happiness(self, pet):
        pet.feed()
        assert pet.hunger == 75
        assert pet.happiness == 55

    def test_never_exceeds_max(self, pet):
        for _ in range(10):
            pet.feed()
        assert pet.hunger == 100
        assert pet.happiness == 100


class TestPlay:
    def test_costs_energy_based_on_stubbornness(self, pet):
        pet.play()
        assert pet.energy == 35
        assert pet.happiness == 70
        assert pet.hunger == 40

    def test_energy_never_below_zero(self, pet):
        for _ in range(10):
            pet.play()
        assert pet.energy == 0
        assert pet.hunger == 0


class TestRest:
    def test_restores_energy(self, pet):
        pet.play()
        pet.rest()
        assert pet.energy == 70
        assert pet.hunger == 35

    def test_energy_never_exceeds_max(self, pet):
        for _ in range(10):
            pet.rest()
        assert pet.energy == 100


class TestSerialization:
    def test_to_dict_contains_all_fields(self, pet):
        data = pet.to_dict()
        expected_keys = {
            "name", "breed", "country", "temperament",
            "stubbornness_score", "description",
            "hunger", "energy", "happiness",
        }
        assert set(data) == expected_keys

    def test_round_trip_keeps_state(self, pet):
        pet.feed()
        pet.play()
        restored = Pet.from_dict(pet.to_dict())
        assert restored.to_dict() == pet.to_dict()

    def test_from_dict_uses_defaults_for_missing_keys(self):
        restored = Pet.from_dict({})
        assert restored.name == "น้องเหมียว"
        assert restored.hunger == 50
