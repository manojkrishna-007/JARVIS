import pyautogui

from tools.base import JarvisTool, ToolResult


class InputTool(JarvisTool):
    """Controls mouse and keyboard input."""

    name = "input"
    description = "Controls the mouse and keyboard."

    def execute(
    self,
    action: str = "",
    x: int | None = None,
    y: int | None = None,
    text: str = "",
    key: str = "",
    keys: list[str] | None = None,
    window=None,
    **kwargs,
) -> ToolResult:
        """Execute a mouse or keyboard action."""

        action = action.strip().lower()

        try:
            if action == "move":
                return self._move_mouse(x, y)

            if action == "move_relative":
                return self._move_mouse_relative(x, y, window,)

            if action == "click":
                return self._click_mouse(x, y)

            if action == "double_click":
                return self._double_click(x, y)

            if action == "type":
                return self._type_text(text)

            if action == "press":
                return self._press_key(key)

            if action == "hotkey":
                return self._hotkey(keys)

            return ToolResult(
                success=False,
                message=f"Unknown input action: {action}",
            )

        except pyautogui.FailSafeException:
            return ToolResult(
                success=False,
                message="Mouse control stopped by the PyAutoGUI fail-safe.",
            )

        except Exception as exc:
            return ToolResult(
                success=False,
                message=f"Input operation failed: {exc}",
            )

    def _move_mouse(
        self,
        x: int | None,
        y: int | None,
    ) -> ToolResult:
        """Move the mouse to a screen coordinate."""

        if x is None or y is None:
            return ToolResult(
                success=False,
                message="Mouse movement requires both X and Y coordinates.",
            )

        pyautogui.moveTo(x, y, duration=0.2)

        return ToolResult(
            success=True,
            message=f"Mouse moved to ({x}, {y}).",
        )

    def _click_mouse(
        self,
        x: int | None,
        y: int | None,
    ) -> ToolResult:
        """Click at a screen coordinate or the current position."""

        if x is not None and y is not None:
            pyautogui.click(x, y)
            return ToolResult(
                success=True,
                message=f"Clicked at ({x}, {y}).",
            )

        pyautogui.click()

        return ToolResult(
            success=True,
            message="Clicked at the current mouse position.",
        )

    def _double_click(
        self,
        x: int | None,
        y: int | None,
    ) -> ToolResult:
        """Double-click at a screen coordinate or current position."""

        if x is not None and y is not None:
            pyautogui.doubleClick(x, y)
            return ToolResult(
                success=True,
                message=f"Double-clicked at ({x}, {y}).",
            )

        pyautogui.doubleClick()

        return ToolResult(
            success=True,
            message="Double-clicked at the current mouse position.",
        )

    def _type_text(self, text: str) -> ToolResult:
        """Type text using the keyboard."""

        if not text:
            return ToolResult(
                success=False,
                message="No text was provided.",
            )

        pyautogui.write(text, interval=0.01)

        return ToolResult(
            success=True,
            message="Text typed successfully.",
        )

    def _press_key(self, key: str) -> ToolResult:
        """Press a single keyboard key."""

        if not key:
            return ToolResult(
                success=False,
                message="No key was specified.",
            )

        pyautogui.press(key)

        return ToolResult(
            success=True,
            message=f"Pressed {key}.",
        )

    def _hotkey(
        self,
        keys: list[str] | None,
    ) -> ToolResult:
        """Press a keyboard shortcut."""

        if not keys:
            return ToolResult(
                success=False,
                message="No keys were specified.",
            )

        pyautogui.hotkey(*keys)

        return ToolResult(
            success=True,
            message=f"Pressed {' + '.join(keys)}.",
        )
        
    def _move_mouse_relative(
        self,
        x,
        y,
        window,
    ) -> ToolResult:
        """Move the mouse relative to a target window."""

        if x is None or y is None:
            return ToolResult(
                success=False,
                message="Relative mouse movement requires X and Y coordinates.",
            )

        if window is None:
            return ToolResult(
                success=False,
                message="No target window was provided.",
            )

        try:
            window_x = window.left
            window_y = window.top

            target_x = window_x + x
            target_y = window_y + y

            pyautogui.moveTo(
                target_x,
                target_y,
                duration=0.2,
            )

            return ToolResult(
                success=True,
                message=(
                    f"Mouse moved to "
                    f"({x}, {y}) relative to the target window."
                ),
            )

        except Exception as exc:
            return ToolResult(
                success=False,
                message=f"Relative mouse movement failed: {exc}",
            )