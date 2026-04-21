"""
Tests for the Decision Engine (routing logic)
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.engine.decision_engine import DecisionEngine
from app.models.schemas import RoutingStrategy


@pytest.fixture
def engine():
    return DecisionEngine()


@pytest.mark.asyncio
async def test_template_routing_on_greeting(engine):
    """High-confidence template match should route to TEMPLATE."""
    with patch.object(engine.template_engine, "match", new_callable=AsyncMock) as mock_t, \
         patch("app.engine.decision_engine.cache_get", return_value=None), \
         patch("app.engine.decision_engine.cache_set", new_callable=AsyncMock):
        mock_t.return_value = {"response": "Hello!", "confidence": 0.95}
        result = await engine.process("hi there")

    assert result["strategy"] == RoutingStrategy.TEMPLATE
    assert result["response"] == "Hello!"
    assert result["confidence"] == 0.95


@pytest.mark.asyncio
async def test_local_llm_routing_on_medium_confidence(engine):
    """Medium template confidence → escalate to Local LLM."""
    with patch.object(engine.template_engine, "match", new_callable=AsyncMock) as mock_t, \
         patch.object(engine.local_llm, "generate", new_callable=AsyncMock) as mock_l, \
         patch("app.engine.decision_engine.cache_get", return_value=None), \
         patch("app.engine.decision_engine.cache_set", new_callable=AsyncMock):
        mock_t.return_value = {"response": "", "confidence": 0.4}
        mock_l.return_value = {"response": "Local LLM answer", "confidence": 0.80}
        result = await engine.process("explain your refund process in detail")

    assert result["strategy"] == RoutingStrategy.LOCAL_LLM
    assert "Local LLM" in result["response"]


@pytest.mark.asyncio
async def test_openai_fallback_when_local_llm_fails(engine):
    """If local LLM raises exception, fall back to OpenAI."""
    with patch.object(engine.template_engine, "match", new_callable=AsyncMock) as mock_t, \
         patch.object(engine.local_llm, "generate", side_effect=Exception("Ollama offline")), \
         patch.object(engine.openai_client, "generate", new_callable=AsyncMock) as mock_o, \
         patch("app.engine.decision_engine.cache_get", return_value=None), \
         patch("app.engine.decision_engine.cache_set", new_callable=AsyncMock):
        mock_t.return_value = {"response": "", "confidence": 0.1}
        mock_o.return_value = {"response": "OpenAI answer", "confidence": 0.95}
        result = await engine.process("very complex multi-part technical question")

    assert result["strategy"] == RoutingStrategy.OPENAI
    assert result["response"] == "OpenAI answer"


@pytest.mark.asyncio
async def test_cache_hit_skips_engines(engine):
    """Cached response should be returned immediately without calling any engine."""
    with patch("app.engine.decision_engine.cache_get", return_value="Cached response"), \
         patch.object(engine.template_engine, "match", new_callable=AsyncMock) as mock_t:
        result = await engine.process("hello")

    mock_t.assert_not_called()
    assert result["response"] == "Cached response"
    assert result["cached"] is True


@pytest.mark.asyncio
async def test_processing_time_is_recorded(engine):
    """Processing time should always be present in result."""
    with patch.object(engine.template_engine, "match", new_callable=AsyncMock) as mock_t, \
         patch("app.engine.decision_engine.cache_get", return_value=None), \
         patch("app.engine.decision_engine.cache_set", new_callable=AsyncMock):
        mock_t.return_value = {"response": "Hi!", "confidence": 0.95}
        result = await engine.process("hello")

    assert "processing_time_ms" in result
    assert result["processing_time_ms"] >= 0
