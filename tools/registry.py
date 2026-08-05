from typing import Dict

from tools.base import JarvisTool, ToolResult


class ToolRegistry:
    """Stores and manages all available JARVIS tools."""

    def __init__(self):
        self._tools: Dict[str, JarvisTool] = {}

    def register(self, tool: JarvisTool) -> None:
        """Register a tool with JARVIS."""

        if tool.name in self._tools:
            raise ValueError(
                f"A tool named '{tool.name}' is already registered."
            )

        self._tools[tool.name] = tool

    def get(self, name: str) -> JarvisTool | None:
        """Retrieve a tool by name."""

        return self._tools.get(name)

    def execute(self, name: str, **kwargs) -> ToolResult:
        """Execute a registered tool."""

        tool = self.get(name)

        if tool is None:
            return ToolResult(
                success=False,
                message=f"Tool '{name}' is not registered."
            )

        try:
            return tool.execute(**kwargs)

        except Exception as exc:
            return ToolResult(
                success=False,
                message=f"Tool '{name}' failed: {exc}"
            )

    def list_tools(self) -> list[JarvisTool]:
        """Return all registered tools."""

        return list(self._tools.values())