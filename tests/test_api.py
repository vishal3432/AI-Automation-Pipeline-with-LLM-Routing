"""
Integration tests for FastAPI routes
"""

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch, MagicMock
from app.main import app


@pytest.fixture
def mock_redis():
    redis = MagicMock()
    redis.incr = AsyncMock(return_value=1)
    redis.expire = AsyncMock(return_value=True)
    redis.get = AsyncMock(return_value=None)
    redis.ping = AsyncMock(return_value=True)
    return redis


@pytest.fixture
def mock_celery_task():
    task = MagicMock()
    task.id = "test-task-id-123"
    return task


@pytest.mark.asyncio
async def test_health_check(mock_redis):
    with patch("app.api.routes.health.get_redis", return_value=mock_redis):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "components" in data


@pytest.mark.asyncio
async def test_submit_message_success(mock_redis, mock_celery_task):
    with patch("app.api.routes.messages.get_redis", return_value=mock_redis), \
         patch("app.api.routes.messages.get_db"), \
         patch("app.api.routes.messages.process_message_task") as mock_task:
        mock_task.delay.return_value = mock_celery_task
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/messages", json={
                "channel": "api",
                "sender_id": "user_123",
                "content": "Hello, I need help!",
            })

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "message_id" in data
    assert data["task_id"] == "test-task-id-123"


@pytest.mark.asyncio
async def test_rate_limit_exceeded(mock_redis):
    mock_redis.incr = AsyncMock(return_value=999)  # Simulate over-limit
    with patch("app.api.routes.messages.get_redis", return_value=mock_redis), \
         patch("app.api.routes.messages.get_db"):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/messages", json={
                "channel": "api",
                "sender_id": "spammer_456",
                "content": "Spam message",
            })

    assert response.status_code == 429


@pytest.mark.asyncio
async def test_invalid_channel_rejected():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/messages", json={
            "channel": "telegram",   # Not a valid ChannelType
            "sender_id": "user_789",
            "content": "Hello",
        })
    assert response.status_code == 422  # Validation error
