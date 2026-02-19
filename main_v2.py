"""
AURA 2.0 - AGI Personal Assistant
Main Entry Point - FULLY INTEGRATED
"""

import asyncio
import logging
import yaml
import os
import signal
import sys
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('data/logs/aura.log')
    ]
)
logger = logging.getLogger(__name__)


class AuraV2:
    """AURA 2.0 - Complete AGI Assistant with integrated LLM"""
    
    def __init__(self):
        self.running = False
        self.config = self._load_config()
        self.llm_server = None
        self.watcher = None
        
        logger.info("=" * 60)
        logger.info("🤖 AURA 2.0 - AGI Assistant Initializing")
        logger.info("=" * 60)
    
    def _load_config(self) -> dict:
        """Load configuration"""
        if os.path.exists("config.yaml"):
            with open("config.yaml", 'r') as f:
                return yaml.safe_load(f)
        return {}
    
    async def start(self):
        """Start AURA 2.0"""
        self.running = True
        
        try:
            # Step 1: Start LLM Server (PERSISTENT BRAIN)
            logger.info("[1/4] Starting LLM Server...")
            from src.brain.llm_server import LLMServer
            
            model_path = self.config.get('llm', {}).get('model_path', '~/llama.cpp/models/sarvam-1.bin')
            self.llm_server = LLMServer(model_path)
            
            if not self.llm_server.start():
                logger.error("❌ Failed to start LLM server!")
                return False
            
            logger.info("✅ LLM Server ready - Model loaded in memory")
            
            # Step 2: Start Watcher
            logger.info("[2/4] Starting Watcher...")
            from src.brain.watcher import Watcher
            
            self.watcher = Watcher(self.config)
            self.watcher.register_handler('call', self._handle_call)
            self.watcher.register_handler('call_auto_answer', self._handle_auto_answer)
            self.watcher.register_handler('notification', self._handle_notification)
            
            await self.watcher.start()
            logger.info("✅ Watcher active")
            
            # Step 3: Start Telegram with LLM integration
            logger.info("[3/4] Starting Telegram Bot with LLM...")
            asyncio.create_task(self._run_telegram())
            logger.info("✅ Telegram Bot starting...")
            
            # Step 4: Ready
            logger.info("[4/4] System ready!")
            logger.info("\n" + "=" * 60)
            logger.info("🎉 AURA 2.0 is RUNNING!")
            logger.info("=" * 60)
            logger.info("\nSend /start to your Telegram bot!")
            logger.info("=" * 60 + "\n")
            
            # Keep running
            while self.running:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
            return False
        
        return True
    
    async def _run_telegram(self):
        """Run Telegram bot with full LLM integration"""
        try:
            from telegram import Update
            from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
            
            token = self.config.get('telegram', {}).get('bot_token', '')
            if not token:
                logger.error("❌ No bot token!")
                return
            
            application = Application.builder().token(token).build()
            
            # /start command
            async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
                logger.info(f"/start from user {update.effective_user.id}")
                await update.message.reply_text(
                    "🤖 *AURA 2.0 - AGI Assistant*\n\n"
                    "I am your secure local assistant running Sarvam AI.\n\n"
                    "*Commands:*\n"
                    "• /start - Show this message\n"
                    "• /status - Check system status\n"
                    "• /stop - Stop the bot\n\n"
                    "Just send me any message and I'll respond using my local AI brain! 🧠",
                    parse_mode='Markdown'
                )
            
            # /status command
            async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
                logger.info(f"/status from user {update.effective_user.id}")
                
                llm_status = "✅ Online" if (self.llm_server and self.llm_server.is_running()) else "❌ Offline"
                watcher_status = "✅ Active" if (self.watcher and self.watcher.running) else "❌ Stopped"
                
                await update.message.reply_text(
                    f"🤖 *AURA 2.0 Status*\n\n"
                    f"🧠 LLM Server: {llm_status}\n"
                    f"👁️ Watcher: {watcher_status}\n"
                    f"📱 System: ✅ Running\n\n"
                    f"_Model: Sarvam AI (Local)_\n"
                    f"_Time: {datetime.now().strftime('%H:%M:%S')}_",
                    parse_mode='Markdown'
                )
            
            # /stop command
            async def stop_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
                logger.info(f"/stop from user {update.effective_user.id}")
                await update.message.reply_text("🛑 Stopping AURA 2.0...")
                self.running = False
                await application.stop()
            
            # Handle messages with LLM
            async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
                user_text = update.message.text
                user_id = update.effective_user.id
                
                logger.info(f"💬 Message from {user_id}: {user_text}")
                
                # Show typing indicator
                await update.message.chat.send_action(action="typing")
                
                try:
                    # Generate response using LLM
                    if self.llm_server and self.llm_server.is_running():
                        # Create prompt for Sarvam AI
                        prompt = f"""You are AURA, a helpful AI assistant running locally on the user's Android phone.
You are secure, private, and fast. Be concise and helpful.

User: {user_text}

AURA:"""
                        
                        # Generate response
                        response = self.llm_server.generate(
                            prompt=prompt,
                            max_tokens=256,
                            temperature=0.7
                        )
                        
                        # Clean up response
                        response = response.strip()
                        if not response or response.startswith("Error"):
                            response = "I'm here! How can I help you today?"
                        
                        logger.info(f"🧠 Generated response: {response[:50]}...")
                        
                        # Send response
                        await update.message.reply_text(response)
                    else:
                        # Fallback if LLM not available
                        await update.message.reply_text(
                            "I'm here! (LLM not connected, using basic mode)"
                        )
                        
                except Exception as e:
                    logger.error(f"Error generating response: {e}")
                    await update.message.reply_text(
                        "Sorry, I encountered an error. Please try again."
                    )
            
            # Error handler
            async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
                logger.error(f"Telegram error: {context.error}")
            
            # Register handlers
            application.add_handler(CommandHandler("start", start_cmd))
            application.add_handler(CommandHandler("status", status_cmd))
            application.add_handler(CommandHandler("stop", stop_cmd))
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_msg))
            application.add_error_handler(error_handler)
            
            # Start
            logger.info("Starting Telegram with LLM integration...")
            await application.initialize()
            await application.start()
            await application.updater.start_polling(drop_pending_updates=True)
            
            # Keep running
            while self.running:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Telegram error: {e}", exc_info=True)
    
    # Event handlers
    async def _handle_call(self, event):
        """Handle incoming call"""
        logger.info(f"📞 Call from {event.data.get('name', 'Unknown')}")
    
    async def _handle_auto_answer(self, event):
        """Auto-answer after 20s"""
        caller = event.data.get('name', 'Unknown')
        logger.info(f"📞 Auto-answering call from {caller}")
    
    async def _handle_notification(self, event):
        """Handle notification"""
        logger.info(f"📱 Notification: {event.data.get('title', '')}")
    
    async def stop(self):
        """Stop AURA"""
        logger.info("\n🛑 Stopping AURA 2.0...")
        self.running = False
        
        if self.watcher:
            await self.watcher.stop()
        
        if self.llm_server:
            self.llm_server.stop()
        
        logger.info("✅ Stopped")
    
    def _signal_handler(self, signum, frame):
        """Handle signals"""
        logger.info(f"\nSignal {signum} received")
        asyncio.create_task(self.stop())
        sys.exit(0)


async def main():
    """Main entry"""
    os.makedirs('data/logs', exist_ok=True)
    os.makedirs('data/memory', exist_ok=True)
    
    aura = AuraV2()
    signal.signal(signal.SIGINT, aura._signal_handler)
    signal.signal(signal.SIGTERM, aura._signal_handler)
    
    try:
        if not await aura.start():
            sys.exit(1)
    except KeyboardInterrupt:
        await aura.stop()
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
