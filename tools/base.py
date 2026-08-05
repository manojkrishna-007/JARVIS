from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class ToolResult:
    """Standard result returned by every JARVIS tool."""

    success: bool
    message: str
    data: Any = None


class JarvisTool(ABC):
    """Base class that every JARVIS tool must implement."""

    name: str = "unnamed_tool"
    description: str = "No description provided."

    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """Execute the tool."""
        raise NotImplementedError