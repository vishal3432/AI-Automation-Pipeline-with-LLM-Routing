"""
Email Client (SMTP via aiosmtplib)
Sends automated email replies via any SMTP provider.
"""

import aiosmtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailClient:
    async def send(self, to: str, subject: str, body: str, html_body: str = None) -> bool:
        """Send a plain-text (and optional HTML) email."""
        msg = MIMEMultipart("alternative")
        msg["From"] = settings.SMTP_FROM
        msg["To"] = to
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))
        if html_body:
            msg.attach(MIMEText(html_body, "html"))

        try:
            await aiosmtplib.send(
                msg,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USER,
                password=settings.SMTP_PASSWORD,
                start_tls=True,
            )
            logger.info(f"Email sent to {to} | subject='{subject}'")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {to}: {e}")
            raise

    async def send_bulk(self, recipients: list[str], subject: str, body: str) -> dict:
        """Send email to multiple recipients and report results."""
        results = {"success": [], "failed": []}
        for recipient in recipients:
            try:
                await self.send(to=recipient, subject=subject, body=body)
                results["success"].append(recipient)
            except Exception:
                results["failed"].append(recipient)
        return results
