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
        
        if "hello" in prompt_lower or "hi" in prompt_lower:
            return "Hello! I am Aura. Your secure local assistant. How can I help you today?"
        elif "who are you" in prompt_lower:
            return "I am Aura, a secure personal assistant that runs locally on your device!"
        elif "what can you do" in prompt_lower:
            return "I can help you with:\n📞 Making phone calls\n💬 Sending WhatsApp messages\n🔒 All while keeping your data secure!"
        elif "call" in prompt_lower:
            return "I can help you make a call. Please confirm you want to make a call."
        elif "message" in prompt_lower or "whatsapp" in prompt_lower:
            return "I can send a WhatsApp message for you. Who do you want to send a message to?"
        else:
            return "I understand. In full mode with Sarvam AI, I would give you a smarter response!"

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
            system_prompt = """You are Aura, a secure local personal assistant. Be helpful, concise, and friendly."""
            
            if history:
                for msg in history:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    full_prompt += f"{role}: {content}\n"
            
            full_prompt = f"System: {system_prompt}\n\nUser: {prompt}\n\nAssistant:"

            # Find llama-cli
            llama_cmd = None
            possible_paths = [
                os.path.expanduser("~/llama.cpp/llama-cli"),
                os.path.expanduser("~/llama.cpp/build/llama-cli"),
                "/data/data/com.termux/files/home/llama.cpp/llama-cli",
                "/data/data/com.termux/files/home/llama.cpp/build/llama-cli",
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    llama_cmd = path
                    break

            # Try which as fallback
            if not llama_cmd:
                result = subprocess.run(["which", "llama-cli"], capture_output=True, text=True)
                if result.returncode == 0:
                    llama_cmd = result.stdout.strip()

            if not llama_cmd:
                logger.warning("llama.cpp not found")
                return "⚠️ Sarvam AI not found. Please run the install script again."

            # Find model
            model_paths = [
                os.path.expanduser(f"~/llama.cpp/models/{self.model_name}"),
                os.path.expanduser(f"~/llama.cpp/models/sarvam-1.bin"),
                os.path.expanduser("~/llama.cpp/models/sarvam-1"),
            ]
            
            model_path = None
            for path in model_paths:
                if os.path.exists(path):
                    model_path = path
                    break

            if not model_path:
                logger.warning(f"Model not found: {self.model_name}")
                return f"⚠️ Model '{self.model_name}' not found. Please check your model file."

            logger.info(f"Running: {llama_cmd} -m {model_path}")

            # Run llama.cpp
            result = subprocess.run(
                [llama_cmd, "-m", model_path, "-p", full_prompt, "-n", "150", "--no-mmap", "-c", "512"],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=os.path.expanduser("~/llama.cpp")
            )
            
            if result.returncode == 0:
                response = result.stdout.strip()
                # Clean up response
                if "Assistant:" in response:
                    response = response.split("Assistant:")[-1].strip()
                return response if response else "I processed your request but have no response."
            else:
                logger.error(f"llama.cpp error: {result.stderr}")
                return f"⚠️ LLM Error: {result.stderr[:100]}"

        except subprocess.TimeoutExpired:
            return "⏱️ LLM took too long to respond. Try again."
        except Exception as e:
            logger.error(f"LLM Error: {e}")
            return f"⚠️ LLM Error: {str(e)[:100]}"
