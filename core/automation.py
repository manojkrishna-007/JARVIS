import time
from dataclasses import dataclass
from typing import Any, Callable

from tools.base import ToolResult


@dataclass
class AutomationAction:
    """Represents one executable JARVIS action."""

    tool: str
    action: str | None = None
    parameters: dict[str, Any] | None = None

    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}


class AutomationEngine:
    """Coordinates multi-step GUI automation."""

    def __init__(self, tools):
        self.tools = tools

    def execute_action(self, action: AutomationAction) -> ToolResult:
        """Execute one action through the tool registry."""

        parameters = dict(action.parameters or {})

        if action.action is not None:
            parameters["action"] = action.action

        return self.tools.execute(
            action.tool,
            **parameters,
        )

    def wait(self, seconds: float) -> None:
        """Pause automation for a controlled amount of time."""

        time.sleep(seconds)

    def wait_until(
        self,
        condition: Callable[[], bool],
        timeout: float = 5.0,
        interval: float = 0.1,
    ) -> bool:
        """Wait until a condition becomes true."""

        start = time.time()

        while time.time() - start < timeout:
            try:
                if condition():
                    return True
            except Exception:
                pass

            time.sleep(interval)

        return False

    def launch_and_focus(
        self,
        application: str,
        window_title: str,
        timeout: float = 5.0,
    ) -> ToolResult:
        """
        Launch an application and focus the newly-created window.

        The window is identified using a before/after snapshot rather
        than assuming the application's launch PID owns its GUI window.
        """

        window_tool = self.tools.get("windows")

        if window_tool is None:
            return ToolResult(
                success=False,
                message="WindowTool is not registered.",
            )

        # Capture windows before launching the application.
        previous_windows = window_tool.get_window_snapshot()

        # Launch the application.
        launch_result = self.execute_action(
            AutomationAction(
                tool="app",
                parameters={
                    "application": application,
                },
            )
        )

        if not launch_result.success:
            return launch_result

        # Wait for the new window to appear.
        deadline = time.time() + timeout
        new_window = None

        while time.time() < deadline:
            result = window_tool.find_new_window(
                previous_windows,
                window_title,
            )

            if result.success:
                new_window = result.data
                break

            self.wait(0.1)

        if new_window is None:
            return ToolResult(
                success=False,
                message=(
                    f"{application} launched, but no new "
                    f"'{window_title}' window was detected."
                ),
            )

        # Focus the exact newly-detected window.
        focus_result = self.execute_action(
            AutomationAction(
                tool="windows",
                action="focus",
                parameters={
                    "title": new_window,
                },
            )
        )

        if not focus_result.success:
            return focus_result

        # Return the target window information.
        return ToolResult(
            success=True,
            message=f"Focused new window: {new_window}",
            data={
                "window_title": new_window,
                "application": application,
            },
        )

    def type_text(
        self,
        text: str,
        delay: float = 0.3,
    ) -> ToolResult:
        """Type text after allowing the focused window to settle."""

        self.wait(delay)

        return self.execute_action(
            AutomationAction(
                tool="input",
                action="type",
                parameters={
                    "text": text,
                },
            )
        )

    def execute_sequence(
        self,
        actions: list[AutomationAction],
    ):
        """Execute actions in order until one fails."""

        results = []

        for index, action in enumerate(actions, start=1):
            result = self.execute_action(action)

            results.append(result)

            if not result.success:
                return {
                    "success": False,
                    "failed_step": index,
                    "results": results,
                    "message": result.message,
                }

        return {
            "success": True,
            "results": results,
            "message": "Automation sequence completed successfully.",
        }