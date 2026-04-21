"""
WhatsApp Cloud API Integration
Sends messages via Meta's WhatsApp Business API.
"""

import httpx
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class WhatsAppClient:
    BASE_URL = "https://graph.facebook.com/v18.0"

    async def send_message(self, to: str, message: str) -> dict:
        url = f"{self.BASE_URL}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {"preview_url": False, "body": message},
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            logger.info(f"WhatsApp message sent to {to} | id={data.get('messages', [{}])[0].get('id')}")
            return data

    async def send_template(self, to: str, template_name: str, language: str = "en_US", components: list = []) -> dict:
        url = f"{self.BASE_URL}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language},
                "components": components,
            },
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()

    async def mark_as_read(self, message_id: str) -> dict:
        url = f"{self.BASE_URL}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id,
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            return response.json()
