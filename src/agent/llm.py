"""
LLM Wrapper for Aura - Fixed paths for new llama.cpp build
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
        logger.info(f"LLM Interface: {provider} ({model_name})")

    async def generate(self, prompt: str, context_history: List[Dict] = None) -> str:
        if self.provider == "ollama":
            return await self._ollama_generate(prompt, context_history)
        elif self.provider == "llama-cpp":
            return self._llamacpp_generate(prompt, context_history)
        elif self.provider == "mock":
            return self._mock_generate(prompt, context_history)
        else:
            return "Error: Unknown LLM provider"

    def _mock_generate(self, prompt: str, history: List[Dict]) -> str:
        prompt_lower = prompt.lower()
        if "hello" in prompt_lower or "hi" in prompt_lower:
            return "Hello! I am Aura. Your secure local assistant!"
        elif "who are you" in prompt_lower:
            return "I am Aura, your secure local assistant!"
        elif "what can you do" in prompt_lower:
            return "I can help with calls, messages, and more!"
        else:
            return "I understand. I am running locally with Sarvam AI!"

    async def _ollama_generate(self, prompt: str, history: List[Dict]) -> str:
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
                        return "Error communicating with LLM."
        except Exception as e:
            logger.error(f"LLM Error: {e}")
            return "LLM is offline."

    def _llamacpp_generate(self, prompt: str, history: List[Dict]) -> str:
        """NEW: Uses build/bin/llama-cli path"""
        try:
            # Build prompt
            system_prompt = "You are Aura, a helpful local assistant."
            full_prompt = f"System: {system_prompt}\n\nUser: {prompt}\n\nAssistant:"

            # Find llama-cli - CHECK NEW BUILD PATH
            llama_paths = [
                "~/llama.cpp/build/bin/llama-cli",
                "~/llama.cpp/llama-cli",
                "~/llama.cpp/build/llama-cli",
            ]
            
            llama_cmd = None
            for path in llama_paths:
                expanded = os.path.expanduser(path)
                if os.path.exists(expanded):
                    llama_cmd = expanded
                    break

            if not llama_cmd:
                logger.warning("llama-cli not found")
                return "⚠️ AI brain not built. Run: bash ~/aura-secure-assistant/scripts/build_llama.sh"

            # Find model
            model_path = os.path.expanduser(f"~/llama.cpp/models/{self.model_name}")
            if not os.path.exists(model_path):
                model_path = os.path.expanduser(f"~/llama.cpp/models/sarvam-1.bin")
            
            if not os.path.exists(model_path):
                return f"⚠️ Model not found: {self.model_name}"

            logger.info(f"Running: {llama_cmd} with {model_path}")

            # Run llama.cpp
            result = subprocess.run(
                [llama_cmd, "-m", model_path, "-p", full_prompt, "-n", "100", "--no-mmap"],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=os.path.expanduser("~/llama.cpp/build")
            )
            
            if result.returncode == 0:
                response = result.stdout.strip()
                if "Assistant:" in response:
                    response = response.split("Assistant:")[-1].strip()
                return response if response else "Processed."
            else:
                logger.error(f"Error: {result.stderr}")
                return f"AI Error: {result.stderr[:50]}"

        except subprocess.TimeoutExpired:
            return "⏱️ AI took too long"
        except Exception as e:
            logger.error(f"Error: {e}")
            return f"Error: {str(e)[:50]}"
