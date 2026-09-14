"""Unit tests ของ APIClient - ทดสอบเฉพาะส่วนที่ไม่ต้องต่ออินเทอร์เน็ต"""

import pytest

from src.api_client import APIClient

SAMPLE_JSON = '[{"breed": "Siamese", "country": "ไทย"}]'


class TestStripCodeFence:
    def test_removes_json_fence(self):
        text = f"```json\n{SAMPLE_JSON}\n```"
        assert APIClient.strip_code_fence(text) == SAMPLE_JSON

    def test_removes_plain_fence(self):
        text = f"```\n{SAMPLE_JSON}\n```"
        assert APIClient.strip_code_fence(text) == SAMPLE_JSON

    def test_keeps_plain_json_unchanged(self):
        assert APIClient.strip_code_fence(f"  {SAMPLE_JSON}  ") == SAMPLE_JSON


class TestParseResponse:
    def test_parses_into_python_objects(self):
        result = APIClient.parse_response(f"```json\n{SAMPLE_JSON}\n```")
        assert result[0]["breed"] == "Siamese"


class TestBuildPrompt:
    def test_prompt_contains_requested_limit(self):
        assert "จำนวน 7 สายพันธุ์" in APIClient.build_prompt(7)


class TestApiKeyGuard:
    @pytest.mark.parametrize("api_key", ["", None])
    def test_rejects_missing_api_key(self, api_key):
        with pytest.raises(ValueError, match="GEMINI_API_KEY"):
            APIClient.get_cats_from_gemini(api_key=api_key)
