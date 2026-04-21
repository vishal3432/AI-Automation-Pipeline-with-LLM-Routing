import hashlib
import hmac
import uuid
import logging

from fastapi import APIRouter, Request, Header, HTTPException
from app.core.config import settings
from app.workers.tasks import process_message_task

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/webhooks/whatsapp", summary="WhatsApp webhook verification")
async def whatsapp_verify(
    hub_mode: str = None,
    hub_challenge: str = None,
    hub_verify_token: str = None,
):
    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_TOKEN:
        logger.info("WhatsApp webhook verified successfully")
        # BUG FIX: returning int(hub_challenge) causes FastAPI to serialize it
        # incorrectly — WhatsApp expects the raw challenge string as plain text.
        from fastapi.responses import PlainTextResponse
        return PlainTextResponse(content=hub_challenge)
    raise HTTPException(status_code=403, detail="Webhook verification failed")


@router.post("/webhooks/whatsapp", summary="Receive WhatsApp messages")
async def whatsapp_webhook(
    request: Request,
    x_hub_signature_256: str = Header(None),
):
    body = await request.body()

    # BUG FIX: hmac.new() is correct Python but the HMAC key for WhatsApp
    # signature validation must be the App Secret, not the verify token.
    # Using WHATSAPP_TOKEN (verify token) here would always fail signature checks.
    # Added WHATSAPP_APP_SECRET to config for this purpose.
    expected_sig = "sha256=" + hmac.new(
        settings.WHATSAPP_APP_SECRET.encode(), body, hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(expected_sig, x_hub_signature_256 or ""):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    data = await request.json()
    processed = 0

    for entry in data.get("entry", []):
        for change in entry.get("changes", []):
            messages = change.get("value", {}).get("messages", [])
            for msg in messages:
                if msg.get("type") == "text":
                    process_message_task.delay(
                        message_id=str(uuid.uuid4()),
                        channel="whatsapp",
                        sender_id=msg["from"],
                        content=msg["text"]["body"],
                        metadata={"wa_message_id": msg["id"]},
                    )
                    processed += 1

    logger.info(f"Dispatched {processed} WhatsApp messages for processing")
    return {"status": "ok", "dispatched": processed}
