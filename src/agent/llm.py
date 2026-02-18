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
            return self._mock_generate(prompt, context_history)
        else:
            return "Error: Unknown LLM provider"

    def _mock_generate(self, prompt: str, history: List[Dict]) -> str:
        """Mock mode - simple responses without LLM."""
        prompt_lower = prompt.lower()
        
        # Simple rule-based responses
        if "hello" in prompt_lower or "hi" in prompt_lower:
            return "Hello! I am Aura. Your secure local assistant. How can I help you today?"
        elif "who are you" in prompt_lower:
            return "I am Aura, a secure personal assistant that runs locally on your device. I help with calls, messages, and more!"
        elif "what can you do" in prompt_lower:
            return "I can help you with:\n📞 Making phone calls\n💬 Sending WhatsApp messages\n📅 Managing calendar\n🔒 All while keeping your data secure and local!"
        elif "call" in prompt_lower:
            return "I can help you make a call. Please confirm you want to make a call."
        elif "message" in prompt_lower or "whatsapp" in prompt_lower:
            return "I can send a WhatsApp message for you. Who do you want to send a message to?"
        else:
            return "I understand your message. In full mode with Sarvam AI, I would give you a smarter response! For now, I'm in basic mode."

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
            llama_cmd = None
            
            # Try common paths
            paths = [
                "llama-cli",
                "./llama-cli",
                "~/llama.cpp/llama-cli",
                "$PREFIX/bin/llama-cli",
                "/data/data/com.termux/files/home/llama.cpp/llama-cli",
                "/data/data/com.termux/files/usr/bin/llama-cli"
            ]
            
            for path in paths:
                expanded = os.path.expandvars(path)
                if os.path.exists(expanded):
                    llama_cmd = expanded
                    break
                # Also try which
                result = subprocess.run(["which", expanded.replace("$PREFIX/", "")], 
                                capture_output=True)
                if result.returncode == 0:
                    llama_cmd = expanded
                    break

            if not llama_cmd:
                logger.warning("llama.cpp not found. Using mock mode.")
                return "Sarvam AI not installed. Using basic mode.\n\nTo install Sarvam AI, run:\ncurl -sL https://raw.githubusercontent.com/AdityaPagare619/aura-secure-assistant/main/scripts/install_sarvam.sh | bash"

            # Check if model exists
            model_path = os.path.expandvars(f"$HOME/llama.cpp/models/{self.model_name}")
            if not os.path.exists(model_path):
                model_path = os.path.expandvars(f"$PREFIX/bin/{self.model_name}")
            if not os.path.exists(model_path):
                return f"Model '{self.model_name}' not found.\nPlace your Sarvam model at: ~/llama.cpp/models/{self.model_name}"

            # Run llama.cpp
            result = subprocess.run(
                [llama_cmd, "-m", model_path, "-p", full_prompt, "-n", "100", "--no-mmap"],
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
