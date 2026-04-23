"""
OpenAI Client
Used only as a last resort — most expensive tier.
"""

import openai
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a professional, empathetic customer support agent. "
    "Give accurate, concise answers under 150 words. "
    "If you cannot help, politely say so and offer to connect the user with a human agent."
)


class OpenAIClient:
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY , base_url="https://api.groq.com/openai/v1")
        self.model = settings.OPENAI_MODEL

    async def process(self, content: str, context: dict = None) -> dict:
        context = context or {}
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Inject conversation history if available
        if context.get("history"):
            messages.extend(context["history"])

        messages.append({"role": "user", "content": content})

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=300,
            temperature=0.7,
        )

        text = response.choices[0].message.content.strip()
        tokens = response.usage.total_tokens

        logger.info(f"OpenAI used {tokens} tokens")

        return {
            "response": text,
            "confidence": 0.95,
            "tokens_used": tokens,
            "model": self.model,
        }
