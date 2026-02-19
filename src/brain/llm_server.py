"""
LLM Server - Persistent AI Brain
Keeps model loaded in memory for fast responses
"""

import subprocess
import logging
import time
import os
import requests
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class LLMServer:
    """
    Manages llama.cpp server process
    Keeps model loaded for instant responses
    """
    
    def __init__(self, model_path: str, host: str = "127.0.0.1", port: int = 8080):
        self.model_path = os.path.expanduser(model_path)
        self.host = host
        self.port = port
        self.process: Optional[subprocess.Popen] = None
        self.base_url = f"http://{host}:{port}"
        
    def start(self) -> bool:
        """Start the LLM server"""
        if self.is_running():
            logger.info("LLM server already running")
            return True
            
        if not os.path.exists(self.model_path):
            logger.error(f"Model not found: {self.model_path}")
            return False
            
        try:
            cmd = [
                os.path.expanduser("~/llama.cpp/build/bin/llama-server"),
                "-m", self.model_path,
                "--host", self.host,
                "--port", str(self.port),
                "-c", "2048",  # Context size
                "-n", "512",   # Max tokens
                "--timeout", "300",
            ]
            
            logger.info(f"Starting LLM server: {cmd[0]}")
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.path.expanduser("~/llama.cpp")
            )
            
            # Wait for server to be ready
            for i in range(30):
                time.sleep(1)
                if self.is_running():
                    logger.info("LLM server started successfully")
                    return True
                    
            logger.error("LLM server failed to start within 30 seconds")
            return False
            
        except Exception as e:
            logger.error(f"Failed to start LLM server: {e}")
            return False
    
    def stop(self):
        """Stop the LLM server"""
        if self.process:
            self.process.terminate()
            self.process.wait(timeout=5)
            self.process = None
            logger.info("LLM server stopped")
    
    def is_running(self) -> bool:
        """Check if server is running and responding"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> str:
        """Generate text using the loaded model"""
        if not self.is_running():
            if not self.start():
                return "Error: LLM server not available"
        
        try:
            response = requests.post(
                f"{self.base_url}/completion",
                json={
                    "prompt": prompt,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "stop": ["User:", "System:"],
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("content", "").strip()
            else:
                logger.error(f"LLM request failed: {response.status_code}")
                return "Error: Generation failed"
                
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            return f"Error: {str(e)}"
    
    def get_status(self) -> Dict[str, Any]:
        """Get server status"""
        return {
            "running": self.is_running(),
            "model": os.path.basename(self.model_path),
            "host": self.host,
            "port": self.port,
            "url": self.base_url
        }
