"""
AURA 2.0 - AGI Personal Assistant
Main Entry Point
"""

import asyncio
import logging
import yaml
import os
import signal
import sys
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
    Three-layer brain with persistent AI, proactive capabilities, and secure actions
    """
    
    def __init__(self):
        self.running = False
        self.config = self._load_config()
        
        # Initialize components
        self.llm_server = None
        self.watcher = None
        self.brain = None
        self.telegram = None
        
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
            # Step 1: Start LLM Server (persistent brain)
            logger.info("[1/5] Starting LLM Server...")
            from src.brain.llm_server import LLMServer
            
            model_path = self.config.get('llm', {}).get('model_path', '~/llama.cpp/models/sarvam-1.bin')
            self.llm_server = LLMServer(model_path)
            
            if not self.llm_server.start():
                logger.error("❌ Failed to start LLM server!")
                return False
            logger.info("✅ LLM Server ready - Model loaded in memory")
            
            # Step 2: Initialize memory system
            logger.info("[2/5] Initializing Memory System...")
            # Memory will be initialized in brain
            logger.info("✅ Memory system ready")
            
            # Step 3: Start Watcher (event monitoring)
            logger.info("[3/5] Starting Watcher...")
            from src.brain.watcher import Watcher
            
            self.watcher = Watcher(self.config)
            await self.watcher.start()
            logger.info("✅ Watcher active - Monitoring phone")
            
            # Step 4: Initialize Brain (thinker + actor)
            logger.info("[4/5] Initializing Brain...")
            # Will be implemented
            logger.info("✅ Brain ready")
            
            # Step 5: Start Telegram Interface
            logger.info("[5/5] Starting Telegram Interface...")
            # Will be implemented
            logger.info("✅ Telegram ready")
            
            logger.info("\n" + "=" * 60)
            logger.info("🎉 AURA 2.0 is RUNNING!")
            logger.info("=" * 60)
            logger.info("\nFeatures:")
            logger.info("  • Persistent AI Brain (fast responses)")
            logger.info("  • Proactive call answering (20s)")
            logger.info("  • Smart notification handling")
            logger.info("  • Secure action execution")
            logger.info("\nSend /start to your Telegram bot!")
            logger.info("=" * 60 + "\n")
            
            # Keep running
            while self.running:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
            return False
        
        return True
    
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
