"""
Decision Engine — Hybrid AI Router
Routes: Template (free) → Local LLM (cheap) → OpenAI (fallback)
"""

import time
import hashlib
import logging

from app.engine.template_engine import TemplateEngine
from app.engine.local_llm import LocalLLMClient
from app.engine.openai_client import OpenAIClient
from app.models.schemas import RoutingStrategy
from app.core.config import settings
from app.core.redis_client import cache_get, cache_set

logger = logging.getLogger(__name__)


class DecisionEngine:
    def __init__(self):
        self.template_engine = TemplateEngine()
        self.local_llm = LocalLLMClient()
        self.openai_client = OpenAIClient()

    async def process(self, content: str, context: dict = None) -> dict:
        context = context or {}
        start = time.time()
        cache_key = f"response:{hashlib.md5(content.lower().strip().encode()).hexdigest()}"

        # 1. Check Redis cache
        cached = await cache_get(cache_key)
        if cached:
            logger.info(f"Cache HIT for key {cache_key}")
            return {
                "response": cached,
                "strategy": RoutingStrategy.TEMPLATE,
                "confidence": 1.0,
                "processing_time_ms": (time.time() - start) * 1000,
                "cached": True,
            }

        # 2. Template Engine (fastest, free)
        template_result = await self.template_engine.process(content, context)
        if template_result["confidence"] >= settings.TEMPLATE_CONFIDENCE_THRESHOLD:
            logger.info(f"Routed via TEMPLATE (conf={template_result['confidence']:.2f})")
            await cache_set(cache_key, template_result["response"], ttl=86400)
            return self._build_result(template_result, RoutingStrategy.TEMPLATE, start)

        # 3. Local LLM (cheap, ~0 cost)
        try:
            local_result = await self.local_llm.process(content, context)
            if local_result["confidence"] >= settings.LOCAL_LLM_CONFIDENCE_THRESHOLD:
                logger.info(f"Routed via LOCAL_LLM (conf={local_result['confidence']:.2f})")
                await cache_set(cache_key, local_result["response"], ttl=3600)
                return self._build_result(local_result, RoutingStrategy.LOCAL_LLM, start)
        except Exception as e:
            logger.warning(f"Local LLM unavailable, escalating to OpenAI: {e}")

        # 4. OpenAI fallback
        logger.info("Routed via OPENAI")
        openai_result = await self.openai_client.process(content, context)
        await cache_set(cache_key, openai_result["response"], ttl=1800)
        return self._build_result(openai_result, RoutingStrategy.OPENAI, start)

    def _build_result(self, result: dict, strategy: RoutingStrategy, start: float) -> dict:
        return {
            "response": result["response"],
            "strategy": strategy,
            "confidence": result.get("confidence", 0.0),
            "processing_time_ms": (time.time() - start) * 1000,
            "cached": False,
        }
