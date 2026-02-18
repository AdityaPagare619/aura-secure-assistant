"""
LLM Wrapper for Aura.
Supports Ollama (easier for mobile) or llama.cpp directly.
"""

import os
import logging
import asyncio
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class LLMInterface:
    def __init__(self, provider: str = "ollama", model_name: str = "sarvam-1"):
        self.provider = provider  # "ollama" or "mock"
        self.model_name = model_name
        logger.info(f"LLM Interface initialized with {provider} ({model_name})")

    async def generate(self, prompt: str, context_history: List[Dict] = None) -> str:
        """
        Generate text response from LLM.
        """
        if self.provider == "ollama":
            return await self._ollama_generate(prompt, context_history)
        elif self.provider == "llama-cpp":
            return self._llamacpp_generate(prompt, context_history)
        elif self.provider == "mock":
            return "I am Aura. I am running locally and securely."  # Simple mock
        else:
            return "Error: Unknown LLM provider"

    async def _ollama_generate(self, prompt: str, history: List[Dict]) -> str:
        """
        Call local Ollama API asynchronously.
        """
        try:
            import aiohttp

            # Construct messages payload
            messages = []
            if history:
                messages.extend(history)
            messages.append({"role": "user", "content": prompt})

            # Ollama API
            timeout = aiohttp.ClientTimeout(total=60)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    "http://localhost:11434/api/chat",
                    json={"model": self.model_name, "messages": messages},
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["message"]["content"]
                    else:
                        error_text = await response.text()
                        logger.error(f"Ollama error: {error_text}")
                        return "Error communicating with LLM."
        except asyncio.TimeoutError:
            logger.error("Ollama request timed out")
            return "LLM took too long to respond."
        except Exception as e:
            logger.error(f"LLM Error: {e}")
            return "LLM is currently offline."

    def _llamacpp_generate(self, prompt: str, history: List[Dict]) -> str:
        """
        Call llama.cpp binary directly (more secure/offline).
        """
        # Placeholder for llama.cpp binary execution
        logger.warning("llama-cpp execution not implemented yet.")
        return "LLM (llama.cpp) execution not implemented."
