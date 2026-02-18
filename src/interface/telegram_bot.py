"""
Telegram Bot Interface for Aura.
Connects Telegram User <-> Aura Agent.
Supports Text and Voice Notes.
"""

import asyncio
import logging
import os
import signal
import sys
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from ..agent.agent import AuraAgent
from .voice import VoiceHandler

logger = logging.getLogger(__name__)


class AuraBot:
    def __init__(self, agent: AuraAgent, token: str):
        self.agent = agent
        self.token = token
        self.voice_handler = VoiceHandler()
        self.app = Application.builder().token(token).build()
        self.running = True

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Hello! I am Aura. Your secure local assistant.\n"
            "You can send me text or voice messages.\n"
            "I am running locally and securely.\n\n"
            "Commands:\n"
            "/start - Start bot\n"
            "/stop - Stop bot\n"
            "/status - Check status"
        )

    async def stop_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Stop the bot - for security emergency stop"""
        await update.message.reply_text("🛑 Stopping Aura Bot...")
        self.running = False
        await self.app.stop()
        await update.message.reply_text("Aura Bot stopped. You can close Termux now.")
        # Give time to send message then exit
        await asyncio.sleep(1)
        sys.exit(0)

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check bot status"""
        llm_status = "Unknown"
        try:
            if self.agent.llm.provider == "mock":
                llm_status = "Mock Mode (Basic)"
            elif self.agent.llm.provider == "llama-cpp":
                llm_status = f"Sarvam AI ({self.agent.llm.model_name})"
            elif self.agent.llm.provider == "ollama":
                llm_status = f"Ollama ({self.agent.llm.model_name})"
        except:
            pass
        
        await update.message.reply_text(
            f"🤖 Aura Status:\n"
            f"- LLM: {llm_status}\n"
            f"- Running: Yes\n"
            f"- Security: Active"
        )

    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming voice notes."""
        if not self.running:
            return
            
        voice = update.message.voice
        if not voice:
            return

        logger.info(f"Received voice note from {update.effective_user.id}")

        file = await context.bot.get_file(voice.file_id)
        file_path = f"temp_{voice.file_id}.ogg"
        await file.download_to_drive(file_path)

        try:
            with open(file_path, "rb") as f:
                text = await self.voice_handler.transcribe(f)

            logger.info(f"Transcribed: {text}")
            response = await self.agent.process_message(text)
            await update.message.reply_text(response)

        except Exception as e:
            logger.error(f"Error handling voice: {e}")
            await update.message.reply_text("Sorry, I couldn't process that voice message.")
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self.running:
            return
            
        user_text = update.message.text
        logger.info(f"Received message: {user_text}")
        response = await self.agent.process_message(user_text)
        await update.message.reply_text(response)

    def run(self):
        # Register handlers
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("stop", self.stop_command))
        self.app.add_handler(CommandHandler("status", self.status_command))

        # Voice handler - must be before text handler
        self.app.add_handler(MessageHandler(filters.VOICE, self.handle_voice))

        # Text handler
        self.app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )

        # Start polling
        print("Aura Bot is running...")
        print("Send /start to your bot on Telegram!")
        self.app.run_polling(poll_interval=1.0)
