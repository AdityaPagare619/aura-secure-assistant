"""
Test Script for Aura Agent
"""

import asyncio
import sys

sys.path.insert(0, ".")

from src.agent.agent import AuraAgent
from src.security.policy import PolicyEngine
from src.tools.base import Tool


class MockTool(Tool):
    def __init__(self):
        super().__init__("mock_tool", "A mock tool")

    async def execute(self, **kwargs):
        return {"status": "success", "message": "Mock executed"}

    def get_parameters(self):
        return {}


async def test_agent():
    policy = PolicyEngine()
    tools = [MockTool()]

    agent = AuraAgent(tools, policy, llm_provider="mock")

    print("Test 1: Sending safe message...")
    response = await agent.process_message("Hello Aura")
    print(f"Response: {response}")
    assert "secure" in response.lower() or "running" in response.lower()
    print("Test 1: PASSED")

    print("\nTest 2: Testing Security Policy (Should be blocked)...")
    # In mock, if prompt has "call", it calls mock_tool.
    # Wait, mock LLM is simple. Let's check policy manually.

    # Check allowed tools
    print(f"Phone tool allowed: {policy.check_tool('phone_call')}")
    print(f"Shell tool allowed: {policy.check_tool('exec_shell')}")

    # Check denylist
    shell_allowed = policy.check_tool("exec_shell")
    assert shell_allowed == False, "Shell should be blocked!"
    print("Test 2: PASSED (Shell blocked)")

    print("\nAll tests passed!")


if __name__ == "__main__":
    asyncio.run(test_agent())
