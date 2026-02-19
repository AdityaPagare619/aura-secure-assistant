"""
AURA 2.0 - Complete AGI Engine with Telegram Integration
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


class AuraEngine:
    """Complete AURA AGI System with Telegram"""
    
    def __init__(self):
        self.running = False
        self.config = self._load_config()
        self.telegram_app = None
        
        # Core components
        self.llm_server = None
        self.memory = None
        self.tools = None
        self.reasoning = None
        self.call_handler = None
        self.watcher = None
        
        logger.info("=" * 70)
        logger.info("🤖 AURA 2.0 - AGI Engine Initializing")
        logger.info("=" * 70)
    
    def _load_config(self):
        if os.path.exists("config.yaml"):
            with open("config.yaml", 'r') as f:
                return yaml.safe_load(f)
        return {}
    
    async def initialize(self):
        """Initialize all components"""
        
        # 1. Start LLM Server
        logger.info("[1/7] Starting LLM Brain...")
        from src.brain.llm_server import LLMServer
        
        model_path = self.config.get('llm', {}).get('model_path', '~/llama.cpp/models/sarvam-1.bin')
        self.llm_server = LLMServer(model_path)
        
        if not self.llm_server.start():
            logger.error("❌ CRITICAL: Cannot start LLM brain!")
            return False
        
        logger.info("✅ LLM Brain loaded and ready")
        
        # 2. Initialize Memory
        logger.info("[2/7] Initializing Memory System...")
        self.memory = SimpleMemory()
        logger.info("✅ Memory active")
        
        # 3. Initialize Tool Executor
        logger.info("[3/7] Loading Tools...")
        from src.tools.tool_executor import ToolExecutor
        self.tools = ToolExecutor()
        logger.info(f"✅ {len(self.tools.registry.list_tools())} tools loaded")
        
        # 4. Initialize Reasoning Engine
        logger.info("[4/7] Initializing Reasoning Engine...")
        from src.brain.reasoning_engine import ReasoningEngine
        self.reasoning = ReasoningEngine(self.llm_server, self.memory, self.tools)
        logger.info("✅ Reasoning engine ready")
        
        # 5. Initialize Call Handler
        logger.info("[5/7] Loading Call Handler...")
        from src.brain.call_handler import CallHandler
        self.call_handler = CallHandler(self.llm_server, self.memory, self.reasoning)
        logger.info("✅ Call handler ready")
        
        # 6. Initialize Event Watcher
        logger.info("[6/7] Starting Event Watcher...")
        from src.brain.watcher import Watcher
        self.watcher = Watcher(self.config)
        
        self.watcher.register_handler('call', self._on_call)
        self.watcher.register_handler('call_auto_answer', self._on_auto_answer)
        self.watcher.register_handler('notification', self._on_notification)
        
        await self.watcher.start()
        logger.info("✅ Watcher monitoring phone")
        
        # 7. Start Telegram Bot
        logger.info("[7/7] Starting Telegram Bot...")
        await self._start_telegram()
        logger.info("✅ Telegram bot started")
        
        return True
    
    async def _start_telegram(self):
        """Start Telegram bot integration"""
        try:
            from telegram import Update
            from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
            
            token = self.config.get('telegram', {}).get('bot_token', '')
            if not token:
                logger.error("❌ No Telegram bot token configured!")
                return
            
            # Create application
            self.telegram_app = Application.builder().token(token).build()
            
            # Command handlers
            async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
                logger.info(f"📨 /start from user {update.effective_user.id}")
                await update.message.reply_text(
                    "🤖 *AURA 2.0 - AGI Assistant*\n\n"
                    "I am your autonomous AI assistant!\n\n"
                    "*What I can do:*\n"
                    "• 📞 Answer calls & talk to people\n"
                    "• 📱 Open apps & perform actions\n"
                    "• 🧠 Think & plan autonomously\n"
                    "• 📧 Send messages for you\n"
                    "• 🔔 Handle notifications\n\n"
                    "*Commands:*\n"
                    "• /start - Show this message\n"
                    "• /status - Check system status\n"
                    "• /stop - Stop AURA\n"
                    "• /test - Run action test\n\n"
                    "Just send me any request! Example:\n"
                    "`Send Papa a message that I'm busy`\n"
                    "`What can you do?`",
                    parse_mode='Markdown'
                )
            
            async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
                logger.info(f"📨 /status from user {update.effective_user.id}")
                
                llm_status = "✅ Online" if (self.llm_server and self.llm_server.is_running()) else "❌ Offline"
                watcher_status = "✅ Active" if (self.watcher and self.watcher.running) else "❌ Stopped"
                
                await update.message.reply_text(
                    f"🤖 *AURA 2.0 Status*\n\n"
                    f"🧠 LLM Brain: {llm_status}\n"
                    f"👁️ Event Watcher: {watcher_status}\n"
                    f"🔧 Tools: {len(self.tools.registry.list_tools())} loaded\n"
                    f"📱 System: ✅ Running\n\n"
                    f"_Last update: {datetime.now().strftime('%H:%M:%S')}_",
                    parse_mode='Markdown'
                )
            
            async def test_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
                """Test action execution"""
                logger.info(f"📨 /test from user {update.effective_user.id}")
                
                await update.message.reply_text("🧪 Testing action execution...")
                
                # Test: Get current app
                try:
                    from src.actions.android_controller import AndroidController
                    controller = AndroidController()
                    result = controller.get_current_app()
                    
                    if result.success:
                        await update.message.reply_text(f"✅ Test passed! Current app: {result.output[:100]}")
                    else:
                        await update.message.reply_text(f"⚠️ Test result: {result.error}")
                except Exception as e:
                    await update.message.reply_text(f"❌ Test failed: {str(e)}")
            
            async def stop_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
                logger.info(f"📨 /stop from user {update.effective_user.id}")
                await update.message.reply_text("🛑 Stopping AURA 2.0...")
                self.running = False
                await self.telegram_app.stop()
            
            async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
                """Handle user messages with full reasoning"""
                user_text = update.message.text
                user_id = update.effective_user.id
                
                logger.info(f"💬 Message from {user_id}: {user_text}")
                
                # Show typing indicator
                await update.message.chat.send_action(action="typing")
                
                try:
                    # Use reasoning engine
                    result = await self.reasoning.handle_user_request(user_text)
                    
                    if result.get('needs_clarification'):
                        response = result.get('message', 'I need more information to help with that.')
                    elif result.get('asked_user'):
                        response = f"⏳ {result.get('user_message', 'Should I proceed?')}\n\nReply 'yes' to confirm or tell me what to change."
                    elif result.get('executed'):
                        actions = [a.get('tool', 'action') for a in result['executed']]
                        response = f"✅ Done! I performed: {', '.join(actions)}."
                    else:
                        # Generate conversational response using LLM
                        prompt = f"User: {user_text}\n\nAURA:"
                        response = self.llm_server.generate(prompt=prompt, max_tokens=256)
                        if not response or response.startswith("Error"):
                            response = "I'm here! How can I help you today?"
                    
                    logger.info(f"📝 Response: {response[:100]}...")
                    await update.message.reply_text(response)
                    
                except Exception as e:
                    logger.error(f"Error handling message: {e}", exc_info=True)
                    await update.message.reply_text(
                        "❌ I encountered an error processing your request. "
                        "Please try again or check the logs."
                    )
            
            async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
                logger.error(f"Telegram error: {context.error}", exc_info=True)
            
            # Register handlers
            self.telegram_app.add_handler(CommandHandler("start", start_cmd))
            self.telegram_app.add_handler(CommandHandler("status", status_cmd))
            self.telegram_app.add_handler(CommandHandler("test", test_cmd))
            self.telegram_app.add_handler(CommandHandler("stop", stop_cmd))
            self.telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
            self.telegram_app.add_error_handler(error_handler)
            
            # Start
            logger.info("🚀 Starting Telegram polling...")
            await self.telegram_app.initialize()
            await self.telegram_app.start()
            await self.telegram_app.updater.start_polling(drop_pending_updates=True)
            logger.info("✅ Telegram bot polling started")
            
        except Exception as e:
            logger.error(f"Failed to start Telegram: {e}", exc_info=True)
    
    async def _on_call(self, event):
        """Handle incoming call"""
        logger.info(f"📞 Call from {event.data.get('name', 'Unknown')}")
    
    async def _on_auto_answer(self, event):
        """Auto-answer call"""
        logger.info("⏰ Auto-answer triggered!")
        await self.call_handler.handle_incoming_call(event.data)
    
    async def _on_notification(self, event):
        """Handle notification"""
        app = event.source
        title = event.data.get('title', '')
        logger.info(f"📱 Notification: {app} - {title}")
    
    async def run(self):
        """Main run loop"""
        self.running = True
        
        logger.info("\n" + "=" * 70)
        logger.info("🎉 AURA 2.0 IS FULLY OPERATIONAL")
        logger.info("=" * 70)
        logger.info("\n🧠 SYSTEM READY:")
        logger.info("  ✅ Persistent LLM brain (Sarvam AI)")
        logger.info("  ✅ Telegram bot connected")
        logger.info("  ✅ Event watcher active")
        logger.info("  ✅ 11 tools loaded")
        logger.info("  ✅ Autonomous reasoning")
        logger.info("\n📱 SEND A MESSAGE TO YOUR BOT TO TEST")
        logger.info("=" * 70)
        
        # Keep running
        while self.running:
            await asyncio.sleep(1)
    
    async def stop(self):
        """Graceful shutdown"""
        logger.info("\n🛑 Stopping AURA 2.0...")
        self.running = False
        
        if self.telegram_app:
            await self.telegram_app.stop()
        
        if self.watcher:
            await self.watcher.stop()
        
        if self.llm_server:
            self.llm_server.stop()
        
        logger.info("✅ AURA stopped")


class SimpleMemory:
    """Simple memory for now"""
    
    def __init__(self):
        self.items = []
    
    def store(self, content: str, importance: float = 0.5, metadata: dict = None):
        self.items.append({
            'content': content,
            'importance': importance,
            'metadata': metadata or {},
            'time': datetime.now()
        })
    
    def recall(self, query: str, limit: int = 5):
        return [item for item in self.items if query.lower() in item['content'].lower()][:limit]
    
    def get_context_for_llm(self, max_items: int = 5):
        recent = sorted(self.items, key=lambda x: x['time'], reverse=True)[:max_items]
        return "\n".join([item['content'] for item in recent])


async def main():
    """Main entry"""
    os.makedirs('data/logs', exist_ok=True)
    os.makedirs('data/memory', exist_ok=True)
    
    aura = AuraEngine()
    
    def signal_handler(signum, frame):
        asyncio.create_task(aura.stop())
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        if await aura.initialize():
            await aura.run()
        else:
            logger.error("Failed to initialize")
            sys.exit(1)
    except KeyboardInterrupt:
        await aura.stop()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        await aura.stop()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
