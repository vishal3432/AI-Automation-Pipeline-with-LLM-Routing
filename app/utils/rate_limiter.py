"""
Redis-based Sliding Window Rate Limiter
Limits requests per sender per minute.
"""

import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class RateLimiter:
    async def check(self, sender_id: str, redis) -> bool:
        """
        Returns True if the request is within the rate limit.
        Uses Redis INCR + TTL for atomic sliding-window counting.
        """
        key = f"rate_limit:{sender_id}"
        try:
            count = await redis.incr(key)
            if count == 1:
                # First request — set 60-second expiry window
                await redis.expire(key, 60)

            allowed = count <= settings.RATE_LIMIT_PER_MINUTE
            if not allowed:
                logger.warning(f"Rate limit exceeded for sender={sender_id} (count={count})")
            return allowed
        except Exception as e:
            logger.error(f"Rate limiter error: {e}")
            return True  # Fail open to avoid blocking legit traffic

    async def get_remaining(self, sender_id: str, redis) -> int:
        """Returns remaining requests allowed in current window."""
        key = f"rate_limit:{sender_id}"
        count = int(await redis.get(key) or 0)
        return max(0, settings.RATE_LIMIT_PER_MINUTE - count)

    async def reset(self, sender_id: str, redis):
        """Manually reset rate limit for a sender (admin use)."""
        await redis.delete(f"rate_limit:{sender_id}")
