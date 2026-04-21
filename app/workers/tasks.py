"""
Celery Tasks
Async message processing pipeline:
  receive → decision engine → integration layer → log
"""

import asyncio
import logging

from app.workers.celery_app import celery_app
from app.engine.decision_engine import DecisionEngine
from app.integrations.whatsapp import WhatsAppClient
from app.integrations.email_client import EmailClient
from app.models.message_log import MessageLog
from app.core.database import AsyncSessionLocal

logger = logging.getLogger(__name__)

_engine = DecisionEngine()
_whatsapp = WhatsAppClient()
_email = EmailClient()


def _run(coro):
    """Run async coroutine in a sync Celery worker context."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(
    bind=True,
    name="app.workers.tasks.process_message_task",
    max_retries=3,
    default_retry_delay=10,
    acks_late=True,
)
def process_message_task(self, message_id: str, channel: str, sender_id: str,
                          content: str, metadata: dict = None):
    """
    Full message processing pipeline:
    1. Run content through Decision Engine
    2. Dispatch response to correct integration
    3. Log result
    """
    try:
        logger.info(f"[{message_id}] Processing via channel={channel}")

        result = _run(_engine.process(content, context={"sender_id": sender_id, **(metadata or {})}))
        response_text = result["response"]
        strategy = result["strategy"]

        if channel == "whatsapp":
            _run(_whatsapp.send_message(to=sender_id, message=response_text))
        elif channel == "email":
            _run(_email.send(to=sender_id, subject="Re: Your Inquiry", body=response_text))
        # channel == "api": response delivered via task result

        # Save to DB
        async def _save_log():
            async with AsyncSessionLocal() as session:
                log = MessageLog(
                    id=message_id,
                    channel=channel,
                    sender_id=sender_id,
                    content=content,
                    response=response_text,
                    routing_strategy=str(strategy.value if hasattr(strategy, "value") else strategy),
                    confidence_score=result.get("confidence", 0.0),
                    processing_time_ms=result["processing_time_ms"],
                    metadata_=metadata or {},
                )
                session.add(log)
                await session.commit()
        _run(_save_log())

        logger.info(
            f"[{message_id}] Done | strategy={strategy} | "
            f"time={result['processing_time_ms']:.1f}ms | cached={result['cached']}"
        )

        return {
            "status": "success",
            "message_id": message_id,
            "strategy": str(strategy),
            "processing_time_ms": result["processing_time_ms"],
        }

    except Exception as exc:
        logger.error(f"[{message_id}] Task failed: {exc}", exc_info=True)
        raise self.retry(exc=exc)
