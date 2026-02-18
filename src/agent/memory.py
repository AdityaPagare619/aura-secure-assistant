"""
Memory and Context Management for Aura.
Inspired by OpenClaw but optimized for local, privacy-first usage.
"""

import json
import logging
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class ConversationMessage:
    def __init__(self, role: str, content: str, timestamp: str = None):
        self.role = role  # "user", "assistant", "system"
        self.content = content
        self.timestamp = timestamp or datetime.now().isoformat()


class ContextManager:
    """
    Manages the conversation history and context window.
    Ensures the LLM has relevant history but respects context limits.
    """

    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.messages: List[ConversationMessage] = []

    def add_message(self, role: str, content: str):
        msg = ConversationMessage(role, content)
        self.messages.append(msg)

        # Keep history within limit
        if len(self.messages) > self.max_history:
            # For simple trimming, we remove oldest.
            # Advanced: Could use importance scoring to keep relevant memories.
            self.messages.pop(0)

        logger.info(f"Context updated. History size: {len(self.messages)}")

    def get_context_for_llm(self) -> List[Dict[str, str]]:
        # Convert to format expected by LLM (e.g. OpenAI style)
        return [{"role": m.role, "content": m.content} for m in self.messages]

    def clear(self):
        self.messages = []
        logger.info("Context cleared.")


class ShortTermMemory:
    """
    Ephemeral memory for the current session.
    Stores small facts (e.g., "User is currently driving").
    """

    def __init__(self):
        self.store: Dict[str, Any] = {}

    def set(self, key: str, value: Any):
        self.store[key] = value
        logger.debug(f"Memory set: {key}")

    def get(self, key: str) -> Any:
        return self.store.get(key)

    def clear(self):
        self.store = {}


class LongTermMemory:
    """
    Persistent memory using local SQLite.
    Stores user preferences, past events, etc.
    """

    def __init__(self, db_path: str = "aura_memory.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        import sqlite3

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS memory 
                     (key TEXT PRIMARY KEY, value TEXT, timestamp TEXT)""")
        conn.commit()
        conn.close()

    def save(self, key: str, value: str):
        import sqlite3

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            "INSERT OR REPLACE INTO memory VALUES (?, ?, ?)",
            (key, value, datetime.now().isoformat()),
        )
        conn.commit()
        conn.close()

    def recall(self, key: str) -> str:
        import sqlite3

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT value FROM memory WHERE key=?", (key,))
        row = c.fetchone()
        conn.close()
        return row[0] if row else None
