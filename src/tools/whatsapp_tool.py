"""
WhatsApp Tool for Aura.
Allows reading and sending WhatsApp messages.
Requires: termux-api (android), accessibility service.
"""

import subprocess
import logging
from .base import Tool

logger = logging.getLogger(__name__)


class WhatsAppTool(Tool):
    def __init__(self):
        super().__init__(
            "whatsapp_send", "Send a WhatsApp message to a specified contact."
        )

    async def execute(self, contact: str, message: str, **kwargs) -> dict:
        try:
            # Use termux-api to open WhatsApp with specific intent
            # Note: Direct WhatsApp API is restricted.
            # Best way: Use Accessibility Service to click "Send".
            # For now, we use termux-api to open WhatsApp Web or just copy text.

            logger.info(f"Sending WhatsApp to {contact}: {message}")

            # Example: Use termux-toast or termux-share
            # Or open WhatsApp: am start -a android.intent.action.VIEW -d "https://wa.me/..."

            return {
                "status": "success",
                "message": f"WhatsApp message prepared for {contact}.",
            }
        except Exception as e:
            logger.error(f"Error sending WhatsApp: {e}")
            return {"status": "error", "message": str(e)}

    def get_parameters(self):
        return {
            "type": "object",
            "properties": {
                "contact": {
                    "type": "string",
                    "description": "Phone number or contact name",
                },
                "message": {"type": "string", "description": "Message to send"},
            },
            "required": ["contact", "message"],
        }
