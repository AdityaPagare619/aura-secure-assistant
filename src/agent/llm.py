"""
LLM Wrapper for Aura.
Supports Ollama (easier for mobile) or llama.cpp directly.
"""

import logging
import json
import subprocess
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class LLMInterface:
    def __init__(self, provider: str = "ollama", model_name: str = "sarvam-1"):
        self.provider = provider  # "ollama" or "llama-cpp"
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
        else:
            return "Error: Unknown LLM provider"

    async def _ollama_generate(self, prompt: str, history: List[Dict]) -> str:
        """
        Call local Ollama API.
        """
        try:
            import requests

            # Construct messages payload
            messages = []
            if history:
                messages.extend(history)
            messages.append({"role": "user", "content": prompt})

            # Ollama API
            # Note: This requires internet for the *first* connection to localhost,
            # but after that, traffic is local.
            # For total isolation, use llama-cpp binary directly.
            response = requests.post(
                "http://localhost:11434/api/chat",
                json={"model": self.model_name, "messages": messages},
                stream=False,
            )

            if response.status_code == 200:
                return response.json()["message"]["content"]
            else:
                logger.error(f"Ollama error: {response.text}")
                return "Error communicating with LLM."
        except Exception as e:
            logger.error(f"LLM Error: {e}")
            return "LLM is currently offline."

    def _llamacpp_generate(self, prompt: str, history: List[Dict]) -> str:
        """
        Call llama.cpp binary directly (more secure/offline).
        """
        # This is a simplified example.
        # In production, use the python bindings 'llama-cpp-python'.

        # Construct prompt from history manually (if needed)
        full_prompt = prompt

        # Run the binary
        # cmd = ["./llama.cpp/llama", "-m", "models/sarvam-1.gguf", "-p", full_prompt]
        # result = subprocess.run(cmd, capture_output=True, text=True)
        # return result.stdout

        return "LLM (llama.cpp) response placeholder."
