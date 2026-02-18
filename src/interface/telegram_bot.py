"""
Telegram Bot Interface for Aura - FIXED
"""

import asyncio
import logging
import os
import sys
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackContext,
)

from ..agent.agent import AuraAgent
from .voice import VoiceHandler

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AuraBot:
    def __init__(self, agent: AuraAgent, token: str):
        self.agent = agent
        self.token = token
        self.voice_handler = VoiceHandler()
        self.running = True
        logger.info("AuraBot initialized")

    async def start_command(self, update: Update, context: CallbackContext):
        logger.info(f"Start command from {update.effective_user.id}")
        await update.message.reply_text(
            "Hello! I am Aura. Your secure local assistant.\n"
            "Commands:\n"
            "/start - Info\n"
            "/stop - Stop bot\n"
            "/status - Check status"
        )

    async def stop_command(self, update: Update, context: CallbackContext):
        logger.info(f"Stop command from {update.effective_user.id}")
        await update.message.reply_text("🛑 Stopping...")
        self.running = False
        await context.application.stop()
        sys.exit(0)

    async def status_command(self, update: Update, context: CallbackContext):
        logger.info(f"Status command from {update.effective_user.id}")
        provider = getattr(self.agent.llm, 'provider', 'unknown')
        model = getattr(self.agent.llm, 'model_name', 'unknown')
        await update.message.reply_text(
            f"🤖 Aura Status:\n"
            f"- LLM: {provider} ({model})\n"
            f"- Running: Yes"
        )

    async def handle_message(self, update: Update, context: CallbackContext):
        if not self.running:
            return
            
        user_text = update.message.text
        user_id = update.effective_user.id
        logger.info(f"Message from {user_id}: {user_text}")
        
        try:
            response = await self.agent.process_message(user_text)
            logger.info(f"Response: {response[:50]}...")
            await update.message.reply_text(response)
        except Exception as e:
            logger.error(f"Error: {e}")
            await update.message.reply_text(f"Error: {str(e)[:50]}")

    async def handle_voice(self, update: Update, context: CallbackContext):
        if not self.running:
            return
        await update.message.reply_text("Voice not supported yet")

    async def error_handler(self, update: object, context: CallbackContext):
        logger.error(f"Error: {context.error}")

    def run(self):
        logger.info("Starting bot...")
        
        # Create application
        self.app = Application.builder().token(self.token).build()
        
        # Add handlers
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("stop", self.stop_command))
        self.app.add_handler(CommandHandler("status", self.status_command))
        self.app.add_handler(MessageHandler(filters.VOICE, self.handle_voice))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Add error handler
        self.app.add_error_handler(self.error_handler)
        
        logger.info("Bot handlers registered")
        
        # Start polling
        print("🤖 Aura Bot is running!")
        print("Open Telegram and send /start")
        
        # Run with proper async
        self.app.run_polling(poll_interval=1.0, drop_pending_updates=True)
