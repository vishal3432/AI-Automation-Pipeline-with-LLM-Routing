"""
Tests for the Template Engine pattern matching
"""

import pytest
from app.engine.template_engine import TemplateEngine


@pytest.fixture
def engine():
    return TemplateEngine()


@pytest.mark.asyncio
async def test_greeting_match(engine):
    result = await engine.process("hello there!")
    assert result["confidence"] > 0.5
    assert "Hello" in result["response"]


@pytest.mark.asyncio
async def test_pricing_match(engine):
    result = await engine.process("how much does it cost?")
    assert result["confidence"] > 0.5
    assert "$" in result["response"] or "pricing" in result["response"].lower()


@pytest.mark.asyncio
async def test_refund_match(engine):
    result = await engine.process("I want a refund")
    assert result["confidence"] > 0.5
    assert "30-day" in result["response"] or "refund" in result["response"].lower()


@pytest.mark.asyncio
async def test_no_match_returns_low_confidence(engine):
    result = await engine.process("xyzzy quantum blockchain nebula")
    assert result["confidence"] < 0.5


@pytest.mark.asyncio
async def test_case_insensitive_match(engine):
    result1 = await engine.process("HELLO")
    result2 = await engine.process("hello")
    assert result1["confidence"] > 0.5
    assert result2["confidence"] > 0.5
