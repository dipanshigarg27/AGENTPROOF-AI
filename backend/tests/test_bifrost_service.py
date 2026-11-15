import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import pytest
from unittest.mock import AsyncMock, patch

from services.bifrost_service import call_model
from unittest.mock import AsyncMock, patch

from services.bifrost_service import call_model
from unittest.mock import AsyncMock, patch

from services.bifrost_service import call_model

# Helper classes to mimic OpenAI response objects
class FakeChoice:
    def __init__(self, content, finish_reason):
        self.message = AsyncMock()
        self.message.content = content
        self.finish_reason = finish_reason

class FakeResponse:
    def __init__(self, content, finish_reason, usage=None):
        self.choices = [FakeChoice(content, finish_reason)]
        self.usage = usage

class FakeUsage:
    def __init__(self, prompt, completion, total):
        self.prompt_tokens = prompt
        self.completion_tokens = completion
        self.total_tokens = total

@pytest.mark.asyncio
async def test_successful_response():
    fake_resp = FakeResponse("Full answer", "stop", FakeUsage(10, 20, 30))
    mock_client = AsyncMock()
    mock_client.chat.completions.create.return_value = fake_resp
    with patch("services.bifrost_service._check_bifrost_available", AsyncMock(return_value=False)):
        with patch("services.bifrost_service._get_client_for_model", return_value=(mock_client, "gpt-4o-mini")):
            result = await call_model("openai/gpt-4o-mini", "test task")
    assert result["status"] == "completed"
    assert result["response_text"] == "Full answer"
    assert result["truncated"] is False
    assert result["error"] is None

@pytest.mark.asyncio
async def test_empty_response_is_failure():
    fake_resp = FakeResponse("", "stop", FakeUsage(5, 0, 5))
    mock_client = AsyncMock()
    mock_client.chat.completions.create.return_value = fake_resp
    with patch("services.bifrost_service._check_bifrost_available", AsyncMock(return_value=False)):
        with patch("services.bifrost_service._get_client_for_model", return_value=(mock_client, "gpt-4o-mini")):
            result = await call_model("openai/gpt-4o-mini", "test task")
    assert result["status"] == "failed"
    assert result["response_text"] is None
    assert "Empty response" in result["error"]

@pytest.mark.asyncio
async def test_whitespace_response_is_failure():
    fake_resp = FakeResponse("   \n\t", "stop", FakeUsage(5, 0, 5))
    mock_client = AsyncMock()
    mock_client.chat.completions.create.return_value = fake_resp
    with patch("services.bifrost_service._check_bifrost_available", AsyncMock(return_value=False)):
        with patch("services.bifrost_service._get_client_for_model", return_value=(mock_client, "gpt-4o-mini")):
            result = await call_model("openai/gpt-4o-mini", "test task")
    assert result["status"] == "failed"
    assert result["response_text"] is None

@pytest.mark.asyncio
async def test_truncated_response_sets_flag():
    fake_resp = FakeResponse("Partial answer", "length", FakeUsage(10, 1000, 1010))
    mock_client = AsyncMock()
    mock_client.chat.completions.create.return_value = fake_resp
    with patch("services.bifrost_service._check_bifrost_available", AsyncMock(return_value=False)):
        with patch("services.bifrost_service._get_client_for_model", return_value=(mock_client, "gpt-4o-mini")):
            result = await call_model("openai/gpt-4o-mini", "test task")
    assert result["status"] == "completed"
    assert result["truncated"] is True
    assert result["response_text"] == "Partial answer"
