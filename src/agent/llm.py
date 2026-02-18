"""
LLM Wrapper for Aura.
Supports Ollama, llama.cpp directly, or mock mode.
"""

import os
import logging
import asyncio
import subprocess
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class LLMInterface:
    def __init__(self, provider: str = "mock", model_name: str = "sarvam-1"):
        self.provider = provider
        self.model_name = model_name
        logger.info(f"LLM Interface initialized with {provider} ({model_name})")

    async def generate(self, prompt: str, context_history: List[Dict] = None) -> str:
        """Generate text response from LLM."""
        if self.provider == "ollama":
            return await self._ollama_generate(prompt, context_history)
        elif self.provider == "llama-cpp":
            return self._llamacpp_generate(prompt, context_history)
        elif self.provider == "mock":
            return "I am Aura. Your secure local assistant."
        else:
            return "Error: Unknown LLM provider"

    async def _ollama_generate(self, prompt: str, history: List[Dict]) -> str:
        """Call local Ollama API asynchronously."""
        try:
            import aiohttp
            messages = []
            if history:
                messages.extend(history)
            messages.append({"role": "user", "content": prompt})

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
        except Exception as e:
            logger.error(f"LLM Error: {e}")
            return "LLM is currently offline."

    def _llamacpp_generate(self, prompt: str, history: List[Dict]) -> str:
        """Call llama.cpp binary directly."""
        try:
            # Build prompt from history
            full_prompt = ""
            if history:
                for msg in history:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    full_prompt += f"{role}: {content}\n"
            full_prompt += f"user: {prompt}\nassistant:"

            # Check if llama.cpp exists
            llama_paths = [
                "llama-cli",
                "llama",
                "./llama-cli",
                "$PREFIX/bin/llama-cli",
                "$PREFIX/bin/llama"
            ]
            
            llama_cmd = None
            for path in llama_paths:
                expanded = os.path.expandvars(path)
                if subprocess.run(["which", expanded.replace("$PREFIX/", "")], 
                                capture_output=True).returncode == 0:
                    llama_cmd = expanded
                    break
            
            if not llama_cmd:
                # Try common termux paths
                for path in ["/data/data/com.termux/files/usr/bin/llama-cli",
                            "/data/data/com.termux/files/usr/bin/llama"]:
                    if os.path.exists(path):
                        llama_cmd = path
                        break

            if not llama_cmd:
                logger.warning("llama.cpp not found. Using mock mode.")
                return "I am Aura. LLM not available."

            # Run llama.cpp
            result = subprocess.run(
                [llama_cmd, "-m", self.model_name, "-p", full_prompt, "-n", "100"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                logger.error(f"llama.cpp error: {result.stderr}")
                return "LLM error occurred."

        except subprocess.TimeoutExpired:
            return "LLM took too long to respond."
        except Exception as e:
            logger.error(f"LLM Error: {e}")
            return "LLM is currently offline."
