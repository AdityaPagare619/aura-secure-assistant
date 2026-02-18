"""
Aura - Secure Local Personal Assistant
Main Entry Point
"""

import asyncio
import logging
import yaml
import os

from src.agent.agent import AuraAgent
from src.security.policy import PolicyEngine
from src.tools.base import Tool
from src.tools.phone_tool import PhoneCallTool
from src.tools.whatsapp_tool import WhatsAppTool
from src.interface.telegram_bot import AuraBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_config():
    if os.path.exists("config.yaml"):
        with open("config.yaml", "r") as f:
            return yaml.safe_load(f)
    return {}


def create_tools(config):
    tools = []
    # Add Phone Tool
    tools.append(PhoneCallTool())
    # Add WhatsApp Tool
    tools.append(WhatsAppTool())
    # Add more tools here (Calendar, etc.)
    return tools


def main():
    logger.info("Starting Aura...")
    config = load_config()

    # 1. Initialize Security Policy
    policy = PolicyEngine()

    # 2. Initialize Tools
    tools = create_tools(config)

    # 3. Initialize Agent
    llm_provider = config.get("llm", {}).get("provider", "mock")
    agent = AuraAgent(tools, policy, llm_provider=llm_provider)

    # 4. Start Telegram Bot
    bot_token = config.get("telegram", {}).get("bot_token")
    if not bot_token:
        logger.error("Telegram bot token not found in config.yaml!")
        return

    bot = AuraBot(agent, bot_token)

    logger.info("Aura is running. Press Ctrl+C to stop.")
    bot.run()


if __name__ == "__main__":
    main()
