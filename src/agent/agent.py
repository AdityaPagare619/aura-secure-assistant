"""
The Core Agent Logic.
Manages the interaction between User, LLM, and Tools.
"""

import asyncio
import logging
import json
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
        llm_provider: str = "ollama",
    ):
        self.tools = {tool.name: tool for tool in tools}
        self.policy = policy_engine
        self.llm = LLMInterface(provider=llm_provider)
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

    async def process_message(self, user_message: str) -> str:
        """
        Main loop: Receive Message -> Think (LLM) -> Act (Tools) -> Respond
        """
        # 1. Add to history
        self.conversation_history.append({"role": "user", "content": user_message})
        self.context.add_message("user", user_message)

        # 2. Construct Prompt for LLM (Mock LLM for now)
        # In reality, this would call self.llm.predict()
        llm_response = await self._mock_llm_call(user_message)

        # Save to memory if important (simplified)
        self.context.add_message("assistant", llm_response.get("text", ""))

        # 3. Check if LLM wants to use a tool
        if "tool_call" in llm_response:
            tool_name = llm_response["tool_name"]
            tool_args = llm_response.get("args", {})

            # 4. Security Check
            if not self.policy.check_tool(tool_name):
                return f"❌ Security Policy: Tool '{tool_name}' is blocked."

            # 5. Sensitive Action Check (Human-in-the-loop)
            risk = self.policy.get_tool_risk(tool_name)
            if risk.value >= ActionRisk.HIGH.value:
                # In real implementation, this would pause and wait for user approval via UI
                # For now, we simulate asking for approval
                approval = input(f"⚠️ Aura wants to use '{tool_name}'. Approve? (y/n): ")
                if approval.lower() != "y":
                    return "Action cancelled by user."

            # 6. Execute Tool
            tool = self.tools.get(tool_name)
            if tool:
                result = await tool.execute(**tool_args)
                # 7. Return result to LLM or directly to user
                return f"Tool executed: {result.get('message', 'Done')}"
            else:
                return "Error: Tool not found."

        # 8. Simple text response
        return llm_response.get("text", "I'm thinking...")

    async def _mock_llm_call(self, prompt: str) -> Dict[str, Any]:
        """
        Mock LLM. Replace this with actual llama.cpp / Ollama call.
        """
        # In reality:
        # context = self.context.get_context_for_llm()
        # response = await self.llm.generate(prompt, context)

        # Simple rule-based fallback for demo
        if "call" in prompt.lower():
            return {
                "tool_call": True,
                "tool_name": "phone_call",
                "args": {"number": "1234567890"},
            }
        return {"text": "I am Aura. I am running locally and securely."}
