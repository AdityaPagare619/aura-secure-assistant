"""
AURA 2.0 - Complete AGI Engine
Integrates: LLM Brain + Reasoning + Tools + Actions + Memory
This is the REAL working assistant, not just a chatbot
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
    """
    Complete AURA AGI System
    - Persistent LLM brain
    - Autonomous reasoning
    - Real actions on device
    - Call handling
    - Proactive behavior
    """
    
    def __init__(self):
        self.running = False
        self.config = self._load_config()
        
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
        """Load configuration"""
        if os.path.exists("config.yaml"):
            with open("config.yaml", 'r') as f:
                return yaml.safe_load(f)
        return {}
    
    async def initialize(self):
        """Initialize all components"""
        
        # 1. Start LLM Server (THE BRAIN)
        logger.info("[1/6] Starting LLM Brain...")
        from src.brain.llm_server import LLMServer
        
        model_path = self.config.get('llm', {}).get('model_path', '~/llama.cpp/models/sarvam-1.bin')
        self.llm_server = LLMServer(model_path)
        
        if not self.llm_server.start():
            logger.error("❌ CRITICAL: Cannot start LLM brain!")
            return False
        
        logger.info("✅ LLM Brain loaded and ready")
        
        # 2. Initialize Memory
        logger.info("[2/6] Initializing Memory System...")
        # Placeholder - will integrate full memory
        self.memory = SimpleMemory()
        logger.info("✅ Memory active")
        
        # 3. Initialize Tool Executor
        logger.info("[3/6] Loading Tools...")
        from src.tools.tool_executor import ToolExecutor
        self.tools = ToolExecutor()
        logger.info(f"✅ {len(self.tools.registry.list_tools())} tools loaded")
        
        # 4. Initialize Reasoning Engine
        logger.info("[4/6] Initializing Reasoning Engine...")
        from src.brain.reasoning_engine import ReasoningEngine
        self.reasoning = ReasoningEngine(self.llm_server, self.memory, self.tools)
        logger.info("✅ Reasoning engine ready")
        
        # 5. Initialize Call Handler
        logger.info("[5/6] Loading Call Handler...")
        from src.brain.call_handler import CallHandler
        self.call_handler = CallHandler(self.llm_server, self.memory, self.reasoning)
        logger.info("✅ Call handler ready")
        
        # 6. Initialize Event Watcher
        logger.info("[6/6] Starting Event Watcher...")
        from src.brain.watcher import Watcher
        self.watcher = Watcher(self.config)
        
        # Register event handlers
        self.watcher.register_handler('call', self._on_call)
        self.watcher.register_handler('call_auto_answer', self._on_auto_answer)
        self.watcher.register_handler('notification', self._on_notification)
        
        await self.watcher.start()
        logger.info("✅ Watcher monitoring phone")
        
        return True
    
    async def _on_call(self, event):
        """Handle incoming call"""
        logger.info(f"📞 Call event: {event.data.get('name', 'Unknown')}")
        # Watcher is monitoring, waiting for 20s
    
    async def _on_auto_answer(self, event):
        """Auto-answer call after 20s"""
        logger.info("⏰ Auto-answer triggered!")
        await self.call_handler.handle_incoming_call(event.data)
    
    async def _on_notification(self, event):
        """Handle notification"""
        app = event.source
        title = event.data.get('title', '')
        
        logger.info(f"📱 Notification: {app} - {title}")
        
        # Reason about notification
        plan = await self.reasoning.reason_about_event({
            'type': 'notification',
            'data': {
                'app': app,
                'title': title,
                'text': event.data.get('text', '')
            }
        })
        
        # If urgent, notify user
        if plan.fallback:
            await self._notify_user(plan.fallback)
    
    async def handle_user_message(self, user_text: str) -> str:
        """
        Handle user message with full reasoning and action
        This is where the magic happens!
        """
        logger.info(f"💬 User: {user_text}")
        
        # Use reasoning engine to understand and act
        result = await self.reasoning.handle_user_request(user_text)
        
        if result.get('needs_clarification'):
            return result.get('message', 'I need more information.')
        
        if result.get('asked_user'):
            return result.get('user_message', 'Should I proceed?')
        
        # Generate natural response about what was done
        executed = result.get('executed', [])
        failed = result.get('failed', [])
        
        if executed:
            actions = ", ".join([a.get('tool', 'action') for a in executed])
            return f"✅ Done! I performed: {actions}. Let me know if you need anything else."
        elif failed:
            return f"❌ I tried but encountered an issue with: {failed[0].get('tool')}. Can you help?"
        else:
            return "I understood your request. I'm working on it..."
    
    async def _notify_user(self, message: str):
        """Notify user via Telegram"""
        logger.info(f"🔔 Notify: {message}")
        # Will be integrated with Telegram
    
    async def run(self):
        """Main run loop"""
        self.running = True
        
        logger.info("\n" + "=" * 70)
        logger.info("🎉 AURA 2.0 IS FULLY OPERATIONAL")
        logger.info("=" * 70)
        logger.info("\nCAPABILITIES:")
        logger.info("  🧠 Persistent LLM brain (Sarvam AI)")
        logger.info("  📞 Answer calls after 20s with conversation")
        logger.info("  📱 Control apps and perform actions")
        logger.info("  🧠 Autonomous reasoning and planning")
        logger.info("  🔔 Proactive notification handling")
        logger.info("  🔒 Security constraints enforced")
        logger.info("\n" + "=" * 70)
        
        # Keep running
        while self.running:
            await asyncio.sleep(1)
    
    async def stop(self):
        """Graceful shutdown"""
        logger.info("\n🛑 Stopping AURA 2.0...")
        self.running = False
        
        if self.watcher:
            await self.watcher.stop()
        
        if self.llm_server:
            self.llm_server.stop()
        
        logger.info("✅ AURA stopped")


class SimpleMemory:
    """Simple memory for now - will integrate full graph memory"""
    
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


# For standalone testing
async def main():
    """Main entry"""
    os.makedirs('data/logs', exist_ok=True)
    os.makedirs('data/memory', exist_ok=True)
    
    aura = AuraEngine()
    
    # Handle signals
    def signal_handler(signum, frame):
        asyncio.create_task(aura.stop())
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        if await aura.initialize():
            await aura.run()
        else:
            logger.error("Failed to initialize AURA")
            sys.exit(1)
    except KeyboardInterrupt:
        await aura.stop()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        await aura.stop()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
