import pygetwindow as gw

from tools.base import JarvisTool, ToolResult


class WindowTool(JarvisTool):
    """Finds and focuses application windows."""

    name = "windows"
    description = "Finds, lists, and focuses application windows."

    def execute(
        self,
        action: str = "",
        title: str = "",
        **kwargs,
    ) -> ToolResult:
        """Execute a window operation."""

        action = action.strip().lower()
        title = title.strip()

        if action == "list":
            return self._list_windows()

        if action == "find":
            return self._find_window(title)

        if action == "focus":
            return self._focus_window(title)

        return ToolResult(
            success=False,
            message=f"Unknown window action: {action}",
        )

    def _list_windows(self) -> ToolResult:
        """List visible application windows."""

        windows = []

        for window in gw.getAllWindows():
            try:
                title = window.title.strip()

                if title:
                    windows.append(title)

            except Exception:
                continue

        windows = sorted(set(windows), key=str.lower)

        return ToolResult(
            success=True,
            message="\n".join(windows)
            if windows
            else "No visible windows found.",
            data=windows,
        )

    def _find_window(self, title: str) -> ToolResult:
        """Find windows whose title contains the requested text."""

        if not title:
            return ToolResult(
                success=False,
                message="No window title was specified.",
            )

        matches = []

        for window in gw.getAllWindows():
            try:
                window_title = window.title.strip()

                if title.lower() in window_title.lower():
                    matches.append(window)

            except Exception:
                continue

        if not matches:
            return ToolResult(
                success=False,
                message=f"No window found matching '{title}'.",
            )

        titles = [
            window.title.strip()
            for window in matches
            if window.title.strip()
        ]

        return ToolResult(
            success=True,
            message=f"Found {len(titles)} matching window(s):\n"
            + "\n".join(f"  {item}" for item in titles),
            data=titles,
        )

    def _focus_window(self, title: str) -> ToolResult:
        """Bring a matching window to the foreground."""

        if not title:
            return ToolResult(
                success=False,
                message="No window title was specified.",
            )

        matches = []

        for window in gw.getAllWindows():
            try:
                window_title = window.title.strip()

                if title.lower() in window_title.lower():
                    matches.append(window)

            except Exception:
                continue

        if not matches:
            return ToolResult(
                success=False,
                message=f"No window found matching '{title}'.",
            )

        window = matches[0]

        try:
            if window.isMinimized:
                window.restore()

            window.activate()

            return ToolResult(
                success=True,
                message=f"Focused window: {window.title}",
            )

        except Exception as exc:
            return ToolResult(
                success=False,
                message=f"Could not focus window: {exc}",
            )