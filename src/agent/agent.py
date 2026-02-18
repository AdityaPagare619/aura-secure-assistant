"""
The Core Agent Logic.
Manages the interaction between User, LLM, and Tools.
"""

import asyncio
import logging
import re
from typing import Dict, Any, List

from ..security.policy import PolicyEngine, ActionRisk
from ..tools.base import Tool
from .memory import ContextManager, ShortTermMemory, LongTermMemory
from .llm import LLMInterface

logger = logging.getLogger(__name__)


class AuraAgent:
    def __init__(
        self,
        tools: List[Tool],
        policy_engine: PolicyEngine,
        llm_provider: str = "mock",
        llm_model: str = "sarvam-1",
    ):
        self.tools = {tool.name: tool for tool in tools}
        self.policy = policy_engine
        self.llm = LLMInterface(provider=llm_provider, model_name=llm_model)
        self.conversation_history = []

        # Memory Systems
        self.context = ContextManager(max_history=10)
        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory()

        # System Prompt defining Aura's persona and rules
        self.system_prompt = """
You are Aura, a secure, local, and privacy-focused personal assistant.
You run entirely on the user's device (AuraPhone).
Your goal is to help the user manage their life: answer calls, track events, read messages.
You are NOT allowed to access the internet or browse the web.
You are NOT allowed to execute shell commands.
Always ask for confirmation before making calls or sending messages.
Be concise and helpful.
"""

    def sanitize_input(self, text: str) -> str:
        """Sanitize user input to prevent Prompt Injection."""
        patterns = [
            r"ignore previous instructions",
            r"disregard system prompt",
            r"you are now",
            r"pretend to be",
            r"// ignore",
        ]

        sanitized = text
        for pattern in patterns:
            sanitized = re.sub(pattern, "[REDACTED]", sanitized, flags=re.IGNORECASE)

        return sanitized

    async def process_message(self, user_message: str) -> str:
        """Main loop: Receive Message -> Think (LLM) -> Act (Tools) -> Respond"""
        # 0. Sanitize Input
        safe_message = self.sanitize_input(user_message)

        # 1. Add to history
        self.conversation_history.append({"role": "user", "content": safe_message})
        self.context.add_message("user", safe_message)

        # 2. Generate response
        context = self.context.get_context_for_llm()
        llm_response_text = await self.llm.generate(safe_message, context)

        # Save to memory
        self.context.add_message("assistant", llm_response_text)

        return llm_response_text
