"""
Template Engine
Fast pattern-matching response system (zero cost).
"""

import re
from difflib import SequenceMatcher


TEMPLATES = {
    "greeting": {
        "patterns": [r"\b(hi|hello|hey|good morning|good afternoon|good evening|howdy)\b"],
        "response": (
            "Hello! 👋 Welcome! How can I assist you today? "
            "Feel free to ask about our products, pricing, or support."
        ),
    },
    "pricing": {
        "patterns": [r"\b(price|cost|how much|pricing|plan|fee|subscription|charge|rate)\b"],
        "response": (
            "Our pricing starts at $29/month for the Starter plan. "
            "We also offer Professional ($79/mo) and Enterprise (custom) plans. "
            "Reply PRICING for a full comparison, or visit our website."
        ),
    },
    "hours": {
        "patterns": [r"\b(hours|timing|open|close|working hours|schedule|available|availability)\b"],
        "response": (
            "We're available Monday–Friday, 9 AM – 6 PM IST. "
            "For urgent support outside these hours, email support@company.com "
            "and we'll respond within 4 hours."
        ),
    },
    "refund": {
        "patterns": [r"\b(refund|return|money back|cancel|cancellation|chargeback)\b"],
        "response": (
            "We offer a 30-day money-back guarantee, no questions asked. "
            "To initiate a refund, reply REFUND or email billing@company.com "
            "with your order ID."
        ),
    },
    "thanks": {
        "patterns": [r"\b(thanks|thank you|thx|ty|appreciate|grateful)\b"],
        "response": (
            "You're welcome! 😊 We're always happy to help. "
            "Is there anything else I can assist you with today?"
        ),
    },
    "contact": {
        "patterns": [r"\b(contact|reach|speak|talk|call|phone|email|human|agent|support)\b"],
        "response": (
            "You can reach our team via:\n"
            "📧 Email: support@company.com\n"
            "📞 Phone: +1-800-XXX-XXXX (Mon–Fri, 9–6 IST)\n"
            "💬 Live chat: Available on our website"
        ),
    },
    "demo": {
        "patterns": [r"\b(demo|trial|test|free|sample|try|preview)\b"],
        "response": (
            "We'd love to show you a demo! 🎯 "
            "You can start a free 14-day trial at our website — no credit card required. "
            "Or reply DEMO to schedule a live walkthrough with our team."
        ),
    },
}


class TemplateEngine:
    async def process(self, content: str, context: dict = None) -> dict:
        context = context or {}
        text = content.lower().strip()
        best_match = {"response": "", "confidence": 0.0}

        for key, template in TEMPLATES.items():
            for pattern in template["patterns"]:
                if re.search(pattern, text, re.IGNORECASE):
                    score = self._score(text, pattern)
                    if score > best_match["confidence"]:
                        best_match = {
                            "response": template["response"],
                            "confidence": min(score, 0.99),
                            "template_key": key,
                        }

        return best_match

    def _score(self, text: str, pattern: str) -> float:
        # Extract first keyword from regex pattern
        keyword = re.sub(r"[\\b()|?+*]", "", pattern).split("|")[0].strip()
        similarity = SequenceMatcher(None, text[:50], keyword).ratio()
        # Boost: exact keyword match gets 0.9+
        return 0.55 + (similarity * 0.45)
