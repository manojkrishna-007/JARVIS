import psutil

from tools.base import JarvisTool, ToolResult


class ProcessTool(JarvisTool):
    """Provides read-only information about running processes."""

    name = "processes"
    description = "Lists and checks applications and processes currently running."

    def execute(
        self,
        action: str = "",
        process_name: str = "",
        **kwargs,
    ) -> ToolResult:
        """Execute a process information operation."""

        action = action.strip().lower()
        process_name = process_name.strip().lower()

        if action == "list":
            return self._list_processes()

        if action == "check":
            return self._check_process(process_name)

        return ToolResult(
            success=False,
            message=f"Unknown process action: {action}",
        )

    def _list_processes(self) -> ToolResult:
        """Return a list of currently running processes."""

        processes = []

        for process in psutil.process_iter(
            ["pid", "name", "username"]
        ):
            try:
                info = process.info

                processes.append(
                    {
                        "pid": info["pid"],
                        "name": info["name"] or "Unknown",
                        "username": info["username"] or "Unknown",
                    }
                )

            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
                psutil.ZombieProcess,
            ):
                continue

        processes.sort(
            key=lambda item: item["name"].lower()
        )

        return ToolResult(
            success=True,
            message=f"Found {len(processes)} running processes.",
            data=processes,
        )

    def _check_process(self, process_name: str) -> ToolResult:
        """Check whether a specific process is running."""

        if not process_name:
            return ToolResult(
                success=False,
                message="No process name was specified.",
            )

        matches = []

        for process in psutil.process_iter(
            ["pid", "name"]
        ):
            try:
                info = process.info
                name = (info["name"] or "").lower()

                if (
                    process_name == name
                    or process_name in name
                ):
                    matches.append(
                        {
                            "pid": info["pid"],
                            "name": info["name"],
                        }
                    )

            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
                psutil.ZombieProcess,
            ):
                continue

        if not matches:
            return ToolResult(
                success=True,
                message=f"{process_name} is not running.",
                data=[],
            )

        lines = [
            f"{process_name} is running:"
        ]

        for match in matches:
            lines.append(
                f"  PID {match['pid']} - {match['name']}"
            )

        return ToolResult(
            success=True,
            message="\n".join(lines),
            data=matches,
        )