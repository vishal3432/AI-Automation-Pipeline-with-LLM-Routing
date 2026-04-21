import redis.asyncio as redis
from app.core.config import settings

redis_client: redis.Redis = None


async def init_redis():
    global redis_client
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


async def get_redis() -> redis.Redis:
    # BUG FIX: redis_client could be None if init_redis() hasn't run yet
    # (e.g. startup failed silently). Raise a clear error instead of letting
    # downstream code crash with AttributeError: 'NoneType' has no attribute 'incr'
    if redis_client is None:
        raise RuntimeError("Redis client is not initialized. Check startup logs.")
    return redis_client


async def cache_set(key: str, value: str, ttl: int = 3600):
    await redis_client.setex(key, ttl, value)


async def cache_get(key: str) -> str | None:
    return await redis_client.get(key)


async def cache_delete(key: str):
    await redis_client.delete(key)
