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
        pid: int | None = None,
        **kwargs,
    ) -> ToolResult:
        """Execute a window operation."""

        action = action.strip().lower()
        title = title.strip()

        if action == "list":
            return self._list_windows()

        if action == "find":
            if pid is not None:
                return self._find_window_by_pid(pid)

            return self._find_window(title)

        if action == "get":
            if pid is not None:
                return self._get_window_by_pid(pid)

            return self._get_window(title)

        if action == "focus":
            if pid is not None:
                return self._focus_window_by_pid(pid)

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

    def _find_window_by_pid(self, pid: int) -> ToolResult:
        """Find a window belonging to a specific process ID."""

        if pid is None:
            return ToolResult(
                success=False,
                message="No process ID was specified.",
            )

        try:
            import win32gui
            import win32process

            matches = []

            def callback(hwnd, _):
                if not win32gui.IsWindowVisible(hwnd):
                    return

                _, window_pid = win32process.GetWindowThreadProcessId(hwnd)

                if window_pid == pid:
                    title = win32gui.GetWindowText(hwnd).strip()

                    if title:
                        matches.append(hwnd)

            win32gui.EnumWindows(callback, None)

            if not matches:
                return ToolResult(
                    success=False,
                    message=f"No visible window found for PID {pid}.",
                )

            hwnd = matches[0]
            title = win32gui.GetWindowText(hwnd).strip()

            return ToolResult(
                success=True,
                message=f"Found window '{title}' for PID {pid}.",
                data=hwnd,
            )

        except Exception as exc:
            return ToolResult(
                success=False,
                message=f"Could not find window for PID {pid}: {exc}",
            )

    def _get_window(self, title: str) -> ToolResult:
        """Return the first matching window object."""

        if not title:
            return ToolResult(
                success=False,
                message="No window title was specified.",
            )

        for window in gw.getAllWindows():
            try:
                window_title = window.title.strip()

                if title.lower() in window_title.lower():
                    return ToolResult(
                        success=True,
                        message=f"Found window: {window_title}",
                        data=window,
                    )

            except Exception:
                continue

        return ToolResult(
            success=False,
            message=f"No window found matching '{title}'.",
        )

    def _get_window_by_pid(self, pid: int) -> ToolResult:
        """Return a pygetwindow object belonging to a process ID."""

        result = self._find_window_by_pid(pid)

        if not result.success:
            return result

        hwnd = result.data

        try:
            window = gw.Win32Window(hwnd)

            return ToolResult(
                success=True,
                message=f"Found window: {window.title}",
                data=window,
            )

        except Exception as exc:
            return ToolResult(
                success=False,
                message=f"Could not create window object: {exc}",
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

    def _focus_window_by_pid(self, pid: int) -> ToolResult:
        """Bring a window belonging to a specific PID to the foreground."""

        result = self._get_window_by_pid(pid)

        if not result.success:
            return result

        window = result.data

        try:
            if window.isMinimized:
                window.restore()

            window.activate()

            return ToolResult(
                success=True,
                message=f"Focused window: {window.title} (PID {pid})",
            )

        except Exception as exc:
            return ToolResult(
                success=False,
                message=f"Could not focus PID {pid}: {exc}",
            )
            
    def get_window_snapshot(self) -> set[str]:
        """Return the titles of currently visible windows."""

        windows = set()

        for window in gw.getAllWindows():
            try:
                title = window.title.strip()

                if title:
                    windows.add(title)

            except Exception:
                continue

        return windows
    
    def find_new_window(self, previous_windows: set[str], title: str = "",) -> ToolResult:
        """Find a newly appearing window not present in the previous snapshot."""

        title = title.strip().lower()

        current_windows = self.get_window_snapshot()

        new_windows = current_windows - previous_windows

        if title:
            new_windows = {
                item
                for item in new_windows
                if title in item.lower()
            }

        if not new_windows:
            return ToolResult(
                success=False,
                message="No new matching window found.",
            )

        selected_title = sorted(
            new_windows,
            key=str.lower,
        )[0]

        return ToolResult(
            success=True,
            message=f"Found new window: {selected_title}",
            data=selected_title,
        )