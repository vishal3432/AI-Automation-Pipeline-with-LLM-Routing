import time
from fastapi import APIRouter, Depends
from app.core.redis_client import get_redis
from app.engine.local_llm import LocalLLMClient

router = APIRouter()
local_llm = LocalLLMClient()


@router.get("/health", summary="System health check")
async def health_check(redis=Depends(get_redis)):
    redis_ok = False
    local_llm_ok = False

    try:
        await redis.ping()
        redis_ok = True
    except Exception:
        pass

    try:
        local_llm_ok = await local_llm.health_check()
    except Exception:
        pass

    all_ok = redis_ok
    return {
        "status": "healthy" if all_ok else "degraded",
        "components": {
            "redis": "ok" if redis_ok else "unavailable",
            "local_llm": "ok" if local_llm_ok else "unavailable",
        },
        "timestamp": time.time(),
    }
