"""
AURA 2.0 - AGI Personal Assistant
Main Entry Point - FIXED VERSION
"""

import asyncio
import logging
import yaml
import os
import signal
import sys
import threading
from datetime import datetime

# Setup logging first
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
    """
    AURA 2.0 - The Complete AGI Assistant
    """
    
    def __init__(self):
        self.running = False
        self.config = self._load_config()
        self.telegram_app = None
        self.watcher = None
        self.llm_server = None
        
        logger.info("=" * 60)
        logger.info("🤖 AURA 2.0 - AGI Assistant Initializing")
        logger.info("=" * 60)
    
    def _load_config(self) -> dict:
        """Load configuration"""
        config_path = "config.yaml"
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        return {}
    
    async def start(self):
        """Start AURA 2.0"""
        self.running = True
        
        try:
            # Step 1: Start LLM Server
            logger.info("[1/4] Starting LLM Server...")
            from src.brain.llm_server import LLMServer
            
            model_path = self.config.get('llm', {}).get('model_path', '~/llama.cpp/models/sarvam-1.bin')
            self.llm_server = LLMServer(model_path)
            
            if not self.llm_server.start():
                logger.warning("⚠️ LLM server not available - will use fallback mode")
            else:
                logger.info("✅ LLM Server ready")
            
            # Step 2: Start Watcher
            logger.info("[2/4] Starting Watcher...")
            from src.brain.watcher import Watcher
            
            self.watcher = Watcher(self.config)
            
            # Register handlers for events
            self.watcher.register_handler('call', self._handle_call)
            self.watcher.register_handler('call_auto_answer', self._handle_auto_answer)
            self.watcher.register_handler('notification', self._handle_notification)
            self.watcher.register_handler('calendar_5min', self._handle_calendar_5min)
            self.watcher.register_handler('calendar_urgent', self._handle_calendar_urgent)
            
            await self.watcher.start()
            logger.info("✅ Watcher active")
            
            # Step 3: Start Telegram Bot (in background thread)
            logger.info("[3/4] Starting Telegram Bot...")
            self.telegram_task = asyncio.create_task(self._run_telegram())
            logger.info("✅ Telegram Bot starting...")
            
            # Step 4: Keep running
            logger.info("[4/4] System ready!")
            logger.info("\n" + "=" * 60)
            logger.info("🎉 AURA 2.0 is RUNNING!")
            logger.info("=" * 60)
            logger.info("\nCommands:")
            logger.info("  /start - Show info")
            logger.info("  /status - Check status")
            logger.info("  /stop - Stop bot")
            logger.info("\nFeatures:")
            logger.info("  • Auto-answer calls after 20s")
            logger.info("  • Monitor notifications")
            logger.info("  • Calendar alerts")
            logger.info("=" * 60 + "\n")
            
            # Keep running
            while self.running:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
            return False
        
        return True
    
    async def _run_telegram(self):
        """Run Telegram bot in async context"""
        try:
            from telegram import Update
            from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
            
            token = self.config.get('telegram', {}).get('bot_token', '')
            if not token or token == "YOUR_BOT_TOKEN_HERE":
                logger.error("❌ No bot token configured!")
                return
            
            # Create application
            application = Application.builder().token(token).build()
            
            # Command handlers
            async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
                logger.info(f"/start from user {update.effective_user.id}")
                await update.message.reply_text(
                    "🤖 *AURA 2.0 - AGI Assistant*\n\n"
                    "I am your secure local assistant.\n\n"
                    "*Commands:*\n"
                    "• /start - Show this message\n"
                    "• /status - Check system status\n"
                    "• /stop - Stop the bot\n\n"
                    "*Features:*\n"
                    "• Answer calls after 20s\n"
                    "• Monitor notifications\n"
                    "• Smart alerts\n\n"
                    "All processing is local and secure! 🔒",
                    parse_mode='Markdown'
                )
            
            async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
                logger.info(f"/status from user {update.effective_user.id}")
                
                llm_status = "✅ Online" if (self.llm_server and self.llm_server.is_running()) else "❌ Offline"
                watcher_status = "✅ Active" if (self.watcher and self.watcher.running) else "❌ Stopped"
                
                await update.message.reply_text(
                    f"🤖 *AURA 2.0 Status*\n\n"
                    f"🧠 LLM Server: {llm_status}\n"
                    f"👁️ Watcher: {watcher_status}\n"
                    f"📱 System: ✅ Running\n\n"
                    f"_Last update: {datetime.now().strftime('%H:%M:%S')}_",
                    parse_mode='Markdown'
                )
            
            async def stop_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
                logger.info(f"/stop from user {update.effective_user.id}")
                await update.message.reply_text("🛑 Stopping AURA 2.0...")
                self.running = False
                await application.stop()
            
            async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
                text = update.message.text
                user_id = update.effective_user.id
                logger.info(f"Message from {user_id}: {text}")
                
                # Echo back for now (will integrate LLM later)
                await update.message.reply_text(
                    f"📨 Received: {text}\n\n"
                    f"_(LLM integration coming in next update)_"
                )
            
            async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
                logger.error(f"Telegram error: {context.error}")
            
            # Register handlers
            application.add_handler(CommandHandler("start", start_cmd))
            application.add_handler(CommandHandler("status", status_cmd))
            application.add_handler(CommandHandler("stop", stop_cmd))
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_msg))
            application.add_error_handler(error_handler)
            
            # Start polling
            logger.info("Starting Telegram polling...")
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
        logger.info(f"📞 Incoming call from {event.data.get('name', 'Unknown')}")
        # Call is ringing, monitoring...
    
    async def _handle_auto_answer(self, event):
        """Auto-answer call after 20s"""
        caller = event.data.get('name', event.data.get('number', 'Unknown'))
        logger.info(f"📞 Auto-answering call from {caller}")
        
        # TODO: Implement actual call answering
        # For now, just log it
        logger.info(f"Would answer call and greet {caller}")
    
    async def _handle_notification(self, event):
        """Handle notification"""
        app = event.source
        title = event.data.get('title', '')
        logger.info(f"📱 Notification from {app}: {title}")
    
    async def _handle_calendar_5min(self, event):
        """5 minute calendar warning"""
        title = event.data.get('title', 'Meeting')
        logger.info(f"📅 5 minute warning: {title}")
    
    async def _handle_calendar_urgent(self, event):
        """Urgent calendar alert"""
        title = event.data.get('title', 'Meeting')
        logger.info(f"📅 URGENT: {title} starting now!")
    
    async def stop(self):
        """Stop AURA 2.0"""
        logger.info("\n🛑 Stopping AURA 2.0...")
        self.running = False
        
        if self.watcher:
            await self.watcher.stop()
        
        if self.llm_server:
            self.llm_server.stop()
        
        logger.info("✅ AURA 2.0 stopped")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"\nReceived signal {signum}")
        asyncio.create_task(self.stop())
        sys.exit(0)


async def main():
    """Main entry point"""
    # Create data directories
    os.makedirs('data/logs', exist_ok=True)
    os.makedirs('data/memory', exist_ok=True)
    
    aura = AuraV2()
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, aura._signal_handler)
    signal.signal(signal.SIGTERM, aura._signal_handler)
    
    try:
        success = await aura.start()
        if not success:
            logger.error("Failed to start AURA 2.0")
            sys.exit(1)
    except KeyboardInterrupt:
        await aura.stop()
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
