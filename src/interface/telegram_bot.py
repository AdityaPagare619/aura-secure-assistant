"""
Telegram Bot Interface for Aura.
Connects Telegram User <-> Aura Agent.
Supports Text and Voice Notes.
"""

import asyncio
import logging
import os
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

        # State for conversation mode
        # If user sends voice, we might want to reply with voice?
        # For now, let's default to text replies for simplicity and speed.

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Hello! I am Aura. Your secure local assistant.\n"
            "You can send me text or voice messages.\n"
            "I am running locally and securely."
        )

    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming voice notes."""
        voice = update.message.voice
        if not voice:
            return

        logger.info(f"Received voice note from {update.effective_user.id}")

        # Download the voice file
        file = await context.bot.get_file(voice.file_id)
        file_path = f"temp_{voice.file_id}.ogg"
        await file.download_to_drive(file_path)

        # Convert to text (STT)
        # Note: In a real scenario, we need ffmpeg to convert OGG to WAV for Whisper
        # For now, assume the voice handler can handle it or we convert manually
        try:
            with open(file_path, "rb") as f:
                text = await self.voice_handler.transcribe(f)

            logger.info(f"Transcribed: {text}")

            # Process text through Agent
            response = await self.agent.process_message(text)

            # Send text response
            await update.message.reply_text(response)

            # Optional: Send Voice Response (TTS)
            # if self.voice_mode_enabled:
            #    audio = await self.voice_handler.speak(response)
            #    await update.message.reply_voice(voice=audio)

        except Exception as e:
            logger.error(f"Error handling voice: {e}")
            await update.message.reply_text(
                "Sorry, I couldn't process that voice message."
            )
        finally:
            # Cleanup
            if os.path.exists(file_path):
                os.remove(file_path)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_text = update.message.text
        logger.info(f"Received message: {user_text}")

        # Process through Aura Agent
        response = await self.agent.process_message(user_text)

        # Reply to user
        await update.message.reply_text(response)

    def run(self):
        # Register handlers
        self.app.add_handler(CommandHandler("start", self.start_command))

        # Voice handler - must be before text handler
        self.app.add_handler(MessageHandler(filters.VOICE, self.handle_voice))

        # Text handler
        self.app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )

        # Start polling
        print("Aura Bot is running...")
        self.app.run_polling(poll_interval=1.0)
