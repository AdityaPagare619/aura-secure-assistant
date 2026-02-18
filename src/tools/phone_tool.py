"""
Phone Control Tools.
Requires 'termux-api' package installed in Termux.
"""

import subprocess
import logging
from .base import Tool

logger = logging.getLogger(__name__)


class PhoneCallTool(Tool):
    def __init__(self):
        super().__init__("phone_call", "Make a phone call to a specified number.")

    async def execute(self, number: str, **kwargs) -> dict:
        try:
            # Use termux-telephony-call
            result = subprocess.run(
                ["termux-telephony-call", number], capture_output=True, text=True
            )
            if result.returncode == 0:
                return {"status": "success", "message": f"Calling {number}..."}
            else:
                return {"status": "error", "message": result.stderr}
        except Exception as e:
            logger.error(f"Error making call: {e}")
            return {"status": "error", "message": str(e)}

    def get_parameters(self):
        return {
            "type": "object",
            "properties": {
                "number": {"type": "string", "description": "Phone number to call"}
            },
            "required": ["number"],
        }


# Placeholder for Answering - Termux cannot answer native calls easily without root/custom ROM
# We can use a VoIP approach or rely on user action if it's a "Smart Dialer" request
# For now, we focus on making calls and reading notifications
