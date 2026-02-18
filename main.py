"""
Aura - Secure Local Personal Assistant
Main Entry Point
"""

import logging
import yaml
import os
from dotenv import load_dotenv

from src.agent.agent import AuraAgent
from src.security.policy import PolicyEngine
from src.tools.phone_tool import PhoneCallTool
from src.tools.whatsapp_tool import WhatsAppTool
from src.interface.telegram_bot import AuraBot

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_config():
    if os.path.exists("config.yaml"):
        with open("config.yaml", "r") as f:
            return yaml.safe_load(f)
    return {}


def get_secret(key, config_dict=None, default=None):
    env_val = os.getenv(key)
    if env_val:
        return env_val
    if config_dict:
        return config_dict.get(key)
    return default


def create_tools(config):
    tools = []
    tools.append(PhoneCallTool())
    tools.append(WhatsAppTool())
    return tools


def main():
    logger.info("Starting Aura...")
    config = load_config()

    policy = PolicyEngine()
    tools = create_tools(config)

    llm_provider = get_secret("LLM_PROVIDER", config.get("llm"), "mock")
    agent = AuraAgent(tools, policy, llm_provider=llm_provider)

    bot_token = get_secret("TELEGRAM_BOT_TOKEN", config.get("telegram"))
    if not bot_token:
        logger.error("Telegram bot token not found!")
        return

    bot = AuraBot(agent, bot_token)

    logger.info("🤖 Aura is running... (Press Ctrl+C to stop)")

    # This blocks and runs the bot
    bot.run()


if __name__ == "__main__":
    main()
