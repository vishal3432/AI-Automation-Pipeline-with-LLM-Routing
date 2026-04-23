"""
Local LLM Client
Connects to Ollama for on-premise LLM inference (Mistral, LLaMA, etc.)
Zero API cost — runs on your own hardware.
"""

import httpx
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a helpful, concise customer support assistant.
- Respond in under 100 words
- Be friendly and professional
- If you don't know something, say so and offer to escalate
- Never make up facts about pricing, policies, or products"""


class LocalLLMClient:
    def __init__(self):
        self.base_url = settings.LOCAL_LLM_URL
        self.model = settings.LOCAL_LLM_MODEL

    async def process(self, content: str, context: dict = None) -> dict:
        context = context or {}
        prompt = f"{SYSTEM_PROMPT}\n\nUser: {content}\nAssistant:"

        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 200,
                    "stop": ["\nUser:", "\n\n"],
                },
            }
            response = await client.post(
                f"{self.base_url}/api/generate", json=payload
            )
            response.raise_for_status()
            data = response.json()

            text = data.get("response", "").strip()
            word_count = len(text.split())
            confidence = min(0.90, 0.60 + (word_count / 100))
            return {
                "response": text,
                "confidence": confidence,
                "model": self.model,
                "eval_count": data.get("eval_count", 0),
            }

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                r = await client.get(f"{self.base_url}/api/tags")
                return r.status_code == 200
        except Exception:
            return False
