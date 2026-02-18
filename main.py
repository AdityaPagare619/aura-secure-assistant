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


def main():
    logger.info("Starting Aura...")
    config = load_config()
    
    logger.info(f"Loaded config: {config}")

    policy = PolicyEngine()
    tools = [PhoneCallTool(), WhatsAppTool()]

    # Get LLM settings - properly handle nested config
    llm_config = config.get("llm", {})
    llm_provider = os.getenv("LLM_PROVIDER", llm_config.get("provider", "mock"))
    llm_model = os.getenv("LLM_MODEL", llm_config.get("model_name", "sarvam-1"))
    
    logger.info(f"LLM: provider={llm_provider}, model={llm_model}")
    
    agent = AuraAgent(tools, policy, llm_provider=llm_provider, llm_model=llm_model)

    # Get Telegram bot token - properly handle nested config
    telegram_config = config.get("telegram", {})
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", telegram_config.get("bot_token"))
    
    logger.info(f"Bot token: {'SET' if bot_token else 'NOT SET'}")
    
    if not bot_token:
        logger.error("Telegram bot token not found!")
        return

    bot = AuraBot(agent, bot_token)

    logger.info("🤖 Aura is running... (Press Ctrl+C to stop)")
    bot.run()


if __name__ == "__main__":
    main()
