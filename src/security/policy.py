"""
Security Policy Engine for Aura.
Implements the "Closed Claw" security model.
"""

import logging
from typing import List, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)


class ActionRisk(Enum):
    LOW = 1  # Reading status, listing files
    MEDIUM = 2  # Sending non-critical messages
    HIGH = 3  # Making calls, sending sensitive data
    CRITICAL = 4  # Changing system settings, deleting data


class PolicyEngine:
    def __init__(self):
        # Define allowed tools (Whitelist approach)
        self.allowed_tools = {
            "read_notifications": ActionRisk.LOW,
            "read_whatsapp": ActionRisk.LOW,
            "send_whatsapp": ActionRisk.MEDIUM,
            "calendar_create": ActionRisk.MEDIUM,
            "phone_call": ActionRisk.HIGH,
            "phone_answer": ActionRisk.HIGH,
            "read_sms": ActionRisk.LOW,
            "send_sms": ActionRisk.MEDIUM,
        }

        # Tools explicitly denied (Blacklist)
        self.denied_tools = [
            "exec_shell",  # No shell access
            "browse_web",  # No web browsing
            "open_url",  # No clicking links
            "access_bank",  # No banking access
            "network_scan",  # No network scanning
        ]

    def check_tool(self, tool_name: str, user_approved: bool = False) -> bool:
        """
        Verify if a tool can be executed.

        Args:
            tool_name: The name of the tool to execute.
            user_approved: Has the user explicitly approved this specific execution instance?

        Returns:
            True if allowed, False otherwise.
        """
        # 1. Check Denylist
        if tool_name in self.denied_tools:
            logger.warning(f"Security Policy: Tool {tool_name} is explicitly denied.")
            return False

        # 2. Check Allowlist
        if tool_name not in self.allowed_tools:
            logger.warning(f"Security Policy: Tool {tool_name} is not in allowlist.")
            return False

        # 3. Check Risk Level vs Approval
        risk_level = self.allowed_tools[tool_name]

        if risk_level.value >= ActionRisk.HIGH.value:
            if not user_approved:
                logger.warning(
                    f"Security Policy: High risk tool {tool_name} requires user approval."
                )
                return False

        return True

    def get_tool_risk(self, tool_name: str) -> ActionRisk:
        return self.allowed_tools.get(tool_name, ActionRisk.CRITICAL)
