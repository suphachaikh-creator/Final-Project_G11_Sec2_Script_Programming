"""Unit tests ของระบบเควสต์ประจำวันและตัวช่วยตกปลา (`src/ai_fishing.py`)

ไม่มีเทสต์ใดยิง Gemini จริง — แทน `requests.post` ด้วยตัวปลอม
และปิด `time.sleep` เพื่อไม่ให้การลองซ้ำต้องรอจริง
"""

import json
import random
from datetime import date

import pytest
import requests

import src.ai_fishing as ai_fishing
from src.ai_fishing import QUEST_TEMPLATES, AIFishingAgent
from src.fish import BRACKISH, FRESHWATER, MARINE, Fish
from src.game_state import GameState
from src.gui.presenter import FishingPresenter, TkClock

TODAY = date(2026, 10, 6)
TOMORROW = date(2026, 10, 7)


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    """ไม่ให้ค่าใน .env ของเครื่องผู้พัฒนาและการรอจริงหลุดเข้ามาในเทสต์"""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setattr(ai_fishing.time, "sleep", lambda seconds: None)


class AllQuestsRng:
    """เลือกเควสต์ครบทั้ง 5 ประเภทตามลำดับเดิม และเลือกตัวแรกเสมอ"""

    def randint(self, low, high):
        return high

    def sample(self, population, count):
        return list(population)[:count]

    def choice(self, options):
        return options[0]


def make_state(bait_level=1, rod_level=1, fish=None):
    return GameState(inventory=fish or [], bait_level=bait_level, rod_level=rod_level)


def make_agent(**kwargs):
    agent = AIFishingAgent(make_state(**kwargs), rng=AllQuestsRng())
    agent.daily_quests(TODAY)
    return agent


def quest(agent, quest_id, today=TODAY):
    return next(q for q in agent.daily_quests(today) if q["id"] == quest_id)


class FakeResponse:
    def __init__(self, payload=None, status_code=200, text=None):
        self.status_code = status_code
        self.ok = status_code < 400
        if text is None and payload is not None:
            text = json.dumps(payload, ensure_ascii=False)
        self._body = {"candidates": [{"content": {"parts": [{"text": text}]}}]}

    def json(self):
        return self._body


class FakePost:
    """แทน requests.post — คืนคำตอบตามลำดับ และจำจำนวนครั้งที่ถูกเรียก"""

    def __init__(self, *responses):
        self.responses = list(responses)
        self.calls = 0

    def __call__(self, url, headers=None, json=None, timeout=None):
        self.calls += 1
        item = self.responses.pop(0) if len(self.responses) > 1 else self.responses[0]
        if isinstance(item, Exception):
            raise item
        return item


def gemini(monkeypatch, *responses):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    fake = FakePost(*responses)
    monkeypatch.setattr(ai_fishing.requests, "post", fake)
    return fake


def ok_quests(*items):
    return FakeResponse({"quests": [{"id": i, "title": t} for i, t in items]})


class TestLocalQuests:
    def test_count_is_between_one_and_five_without_duplicates(self):
        for seed in range(60):
            agent = AIFishingAgent(make_state(), rng=random.Random(seed))
            quests = agent.daily_quests(TODAY)
            ids = [q["id"] for q in quests]
            assert 1 <= len(quests) <= 5
            assert len(ids) == len(set(ids))

    def test_same_day_returns_the_same_set(self):
        agent = AIFishingAgent(make_state(), rng=random.Random(1))
        assert agent.daily_quests(TODAY) == agent.daily_quests(TODAY)

    def test_a_new_day_creates_a_new_set(self):
        agent = make_agent()
        tomorrow = agent.daily_quests(TOMORROW)
        assert all(q["date"] == TOMORROW.isoformat() for q in tomorrow)

    def test_generated_set_is_saved_into_the_game_state(self):
        agent = make_agent()
        assert agent.state.quest_data["date"] == TODAY.isoformat()
        assert len(agent.state.quest_data["quests"]) == len(QUEST_TEMPLATES)


class TestDifficultyAndReward:
    """สูตรใน reports/sprint3_report.md หัวข้อ 8.4"""

    def test_starting_gear(self):
        agent = make_agent()
        assert quest(agent, "any_fish")["target"] == 2
        assert quest(agent, "any_fish")["reward"] == 60 + 25 * 2
        assert quest(agent, "marine")["reward"] == 90 + 25 * 2
        heavy = quest(agent, "heavy_fish")
        assert heavy["target"] == 1
        assert heavy["min_weight"] == pytest.approx(4.0)
        assert heavy["reward"] == 140 + 25 * 1

    def test_upgraded_gear_raises_target_weight_and_reward(self):
        agent = make_agent(bait_level=3, rod_level=2)  # level_score = 3
        assert quest(agent, "any_fish")["target"] == 5
        assert quest(agent, "any_fish")["reward"] == 60 + 25 * 5 + 20 * 3
        heavy = quest(agent, "heavy_fish")
        assert heavy["target"] == 2
        assert heavy["min_weight"] == pytest.approx(4.0 + 1.0 + 1.5)
        assert heavy["reward"] == 140 + 25 * 2 + 20 * 3

    def test_descriptions_are_thai_sentences(self):
        agent = make_agent()
        text = AIFishingAgent.quest_description(quest(agent, "brackish"))
        assert "ปากแม่น้ำน้ำกร่อย" in text
        assert "4.0 กก." in AIFishingAgent.quest_description(quest(agent, "heavy_fish"))


class TestProgressAndReward:
    def test_one_fish_can_count_for_several_quests(self):
        agent = make_agent()
        agent.record_catch(Fish("Tuna", MARINE, 7.0, 100), TODAY)
        assert quest(agent, "marine")["progress"] == 1
        assert quest(agent, "any_fish")["progress"] == 1
        assert quest(agent, "heavy_fish")["progress"] == 1
        assert quest(agent, "freshwater")["progress"] == 0
        assert quest(agent, "brackish")["progress"] == 0

    def test_light_fish_does_not_count_for_the_heavy_quest(self):
        agent = make_agent()
        agent.record_catch(Fish("Goby", FRESHWATER, 1.0, 10), TODAY)
        assert quest(agent, "heavy_fish")["progress"] == 0

    def test_progress_stops_at_the_target(self):
        agent = make_agent()
        for _ in range(5):
            agent.record_catch(Fish("Mullet", BRACKISH, 1.0, 10), TODAY)
        assert quest(agent, "brackish")["progress"] == quest(agent, "brackish")["target"]

    def test_unfinished_quest_pays_nothing(self):
        agent = make_agent()
        money = agent.state.money
        assert agent.claim_reward("any_fish", TODAY) == 0
        assert agent.state.money == money

    def test_finished_quest_pays_once(self):
        agent = make_agent()
        for _ in range(2):
            agent.record_catch(Fish("Carp", FRESHWATER, 1.0, 10), TODAY)
        money = agent.state.money
        reward = agent.claim_reward("freshwater", TODAY)
        assert reward == quest(agent, "freshwater")["reward"]
        assert agent.state.money == money + reward
        assert agent.claim_reward("freshwater", TODAY) == 0
        assert quest(agent, "freshwater")["claimed"] is True

    def test_unknown_quest_id_pays_nothing(self):
        assert make_agent().claim_reward("dragon", TODAY) == 0


class TestSaveFile:
    def test_progress_survives_save_and_load(self):
        agent = make_agent()
        agent.record_catch(Fish("Carp", FRESHWATER, 1.0, 10), TODAY)
        loaded = GameState.from_dict(json.loads(json.dumps(agent.state.to_dict())))
        again = AIFishingAgent(loaded, rng=AllQuestsRng())
        assert quest(again, "freshwater")["progress"] == 1

    def test_old_save_without_quest_data_still_loads(self):
        state = GameState.from_dict({"money": 50, "inventory": []})
        assert state.quest_data == {}
        assert AIFishingAgent(state).daily_quests(TODAY)

    @pytest.mark.parametrize("broken", [[1, 2], "oops", 7, None])
    def test_broken_quest_data_does_not_crash(self, broken):
        state = GameState.from_dict({"quest_data": broken})
        assert state.quest_data == {}
        assert AIFishingAgent(state).daily_quests(TODAY)

    @pytest.mark.parametrize("quests", [
        [{"id": "any_fish"}],
        ["not a quest"],
        [],
        [{"id": "marine", "kind": "location", "location": "moon", "title": "x",
          "claimed": False, "target": 1, "progress": 0, "reward": 1, "min_weight": 1}],
    ])
    def test_malformed_saved_quests_are_regenerated(self, quests):
        state = make_state()
        state.quest_data = {"date": TODAY.isoformat(), "quests": quests}
        agent = AIFishingAgent(state, rng=AllQuestsRng())
        assert len(agent.daily_quests(TODAY)) == len(QUEST_TEMPLATES)


class FakeSpeciesApi:
    def __init__(self, *names):
        self.names = list(names)

    def random_species(self, location, rng=None):
        return {"name": self.names.pop(0), "location": location}


class TestChooseSpecies:
    def test_prefers_the_species_caught_least(self):
        bag = [Fish("Carp", FRESHWATER, 1, 1), Fish("Carp", FRESHWATER, 1, 1),
               Fish("Pike", FRESHWATER, 1, 1)]
        agent = AIFishingAgent(make_state(fish=bag), rng=AllQuestsRng())
        api = FakeSpeciesApi("Carp", "Pike", "Perch")
        assert agent.choose_species(api, FRESHWATER)["name"] == "Perch"

    def test_only_counts_fish_from_the_same_location(self):
        bag = [Fish("Perch", MARINE, 1, 1)]
        agent = AIFishingAgent(make_state(fish=bag), rng=AllQuestsRng())
        api = FakeSpeciesApi("Perch", "Carp", "Carp")
        assert agent.choose_species(api, FRESHWATER)["name"] == "Perch"


class TestGemini:
    def test_without_a_key_it_raises_and_never_calls_the_network(self, monkeypatch):
        fake = FakePost(ok_quests(("marine", "x")))
        monkeypatch.setattr(ai_fishing.requests, "post", fake)
        agent = make_agent()
        assert agent.gemini_configured is False
        with pytest.raises(RuntimeError):
            agent.generate_gemini_quests(TODAY)
        assert fake.calls == 0

    def test_titles_come_from_gemini_but_numbers_come_from_the_game(self, monkeypatch):
        response = FakeResponse({"quests": [
            {"id": "marine", "title": "ล่าฉลามยามเช้า", "target": 999},
            {"id": "any_fish", "title": "ตกอะไรก็ได้"},
        ]})
        gemini(monkeypatch, response)
        agent = make_agent()
        quests = agent.generate_gemini_quests(TODAY)
        assert [q["title"] for q in quests] == ["ล่าฉลามยามเช้า", "ตกอะไรก็ได้"]
        assert quests[0]["target"] == 2
        assert agent.ai_connected is True and agent.ai_checked is True

    def test_long_titles_are_cut_to_32_characters(self, monkeypatch):
        gemini(monkeypatch, ok_quests(("marine", "ก" * 50)))
        quests = make_agent().generate_gemini_quests(TODAY)
        assert len(quests[0]["title"]) == 32

    def test_apply_false_only_checks_the_connection(self, monkeypatch):
        gemini(monkeypatch, ok_quests(("marine", "ทดสอบ")))
        agent = make_agent()
        before = agent.daily_quests(TODAY)
        assert agent.generate_gemini_quests(TODAY, apply=False) is True
        assert agent.daily_quests(TODAY) == before

    @pytest.mark.parametrize("response", [
        ok_quests(("marine", "a"), ("marine", "b")),
        ok_quests(("dragon", "a")),
        ok_quests(*[(t["id"], "x") for t in QUEST_TEMPLATES], ("marine", "y")),
        FakeResponse({"quests": []}),
        FakeResponse({"quests": [{"id": "marine", "title": "  "}]}),
        FakeResponse(text="ไม่ใช่ JSON"),
    ])
    def test_invalid_answers_are_rejected(self, monkeypatch, response):
        gemini(monkeypatch, response)
        with pytest.raises(RuntimeError):
            make_agent().generate_gemini_quests(TODAY)

    def test_temporary_503_is_retried_three_times(self, monkeypatch):
        fake = gemini(monkeypatch, FakeResponse(status_code=503))
        with pytest.raises(RuntimeError, match="503"):
            make_agent().generate_gemini_quests(TODAY)
        assert fake.calls == 3

    def test_succeeds_after_one_temporary_failure(self, monkeypatch):
        fake = gemini(monkeypatch, FakeResponse(status_code=503),
                      ok_quests(("brackish", "ปากแม่น้ำ")))
        quests = make_agent().generate_gemini_quests(TODAY)
        assert fake.calls == 2
        assert quests[0]["id"] == "brackish"

    def test_timeouts_become_a_runtime_error(self, monkeypatch):
        fake = gemini(monkeypatch, requests.Timeout("ช้า"))
        with pytest.raises(RuntimeError):
            make_agent().generate_gemini_quests(TODAY)
        assert fake.calls == 3

    @pytest.mark.parametrize("status, word", [(403, "API key"), (404, "โมเดล"), (400, "400")])
    def test_permanent_http_errors_are_not_retried(self, monkeypatch, status, word):
        fake = gemini(monkeypatch, FakeResponse(status_code=status))
        with pytest.raises(RuntimeError, match=word):
            make_agent().generate_gemini_quests(TODAY)
        assert fake.calls == 1

    def test_cannot_replace_quests_after_progress_without_force(self, monkeypatch):
        gemini(monkeypatch, ok_quests(("marine", "ใหม่")))
        agent = make_agent()
        agent.record_catch(Fish("Tuna", MARINE, 1.0, 10), TODAY)
        with pytest.raises(RuntimeError):
            agent.generate_gemini_quests(TODAY)
        assert agent.generate_gemini_quests(TODAY, force=True)[0]["title"] == "ใหม่"


class QuestRng:
    """ตัวสุ่มของมินิเกม (ตัวอักษร 'a' สองตัว) ที่เลือกชนิดปลาตัวแรกเสมอ"""

    def randint(self, low, high):
        return 2

    def choice(self, options):
        return options[0] if isinstance(options[0], dict) else "a"

    def uniform(self, low, high):
        return 2.0


class TestFishingPresenterIntegration:
    def test_a_caught_fish_moves_the_quest_forward(self):
        state = make_state()
        agent = AIFishingAgent(state, rng=AllQuestsRng())
        api = FakeSpeciesApi("Carp", "Carp", "Carp")
        presenter = FishingPresenter(state, api, rng=QuestRng(), clock=TkClock(1000),
                                     ai_agent=agent)
        presenter.start(FRESHWATER)
        presenter.press("a")
        presenter.press("a")
        result = presenter.finish()
        assert result["success"] is True
        progress = {q["id"]: q["progress"] for q in result["quest"]}
        assert progress["freshwater"] == 1
        assert progress["any_fish"] == 1

    def test_without_an_agent_nothing_changes(self):
        state = make_state()
        presenter = FishingPresenter(state, FakeSpeciesApi("Carp"), rng=QuestRng(),
                                     clock=TkClock(1000))
        presenter.start(FRESHWATER)
        presenter.press("a")
        presenter.press("a")
        result = presenter.finish()
        assert "quest" not in result
        assert state.quest_data == {}
