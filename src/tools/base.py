"""
Base Tool Interface for Aura.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class Tool(ABC):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool with given arguments."""
        pass

    def get_schema(self) -> Dict[str, Any]:
        """Return the JSON schema for the tool."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.get_parameters(),
        }

    @abstractmethod
    def get_parameters(self) -> Dict[str, Any]:
        pass
