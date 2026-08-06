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
        
        if action == "system_usage":
            return self._system_usage()

        if action == "top_cpu":
            return self._top_processes("cpu")

        if action == "top_memory":
            return self._top_processes("memory")

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
        
    def _system_usage(self) -> ToolResult:
        """Return current CPU and memory usage."""

        cpu_percent = psutil.cpu_percent(interval=1)

        memory = psutil.virtual_memory()

        total_gb = memory.total / (1024 ** 3)
        used_gb = memory.used / (1024 ** 3)
        available_gb = memory.available / (1024 ** 3)

        message = (
            f"CPU usage: {cpu_percent:.1f}%\n"
            f"Memory usage: {memory.percent:.1f}%\n"
            f"Memory used: {used_gb:.2f} GB / {total_gb:.2f} GB\n"
            f"Memory available: {available_gb:.2f} GB"
        )

        return ToolResult(
            success=True,
            message=message,
            data={
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used_gb": used_gb,
                "memory_total_gb": total_gb,
                "memory_available_gb": available_gb,
            },
        )
        
    def _top_processes(self, metric: str) -> ToolResult:
        """Return processes using the most CPU or memory."""

        processes = []

        for process in psutil.process_iter(
            ["pid", "name"]
        ):
            try:
                if metric == "cpu":
                    value = process.cpu_percent(
                        interval=0.1
                    )
                else:
                    value = process.memory_percent()

                processes.append(
                    {
                        "pid": process.info["pid"],
                        "name": process.info["name"] or "Unknown",
                        "value": value,
                    }
                )

            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
                psutil.ZombieProcess,
            ):
                continue

        processes.sort(
            key=lambda item: item["value"],
            reverse=True,
        )

        top_processes = processes[:10]

        if metric == "cpu":
            title = "Top CPU-consuming processes:"
            suffix = "% CPU"
        else:
            title = "Top memory-consuming processes:"
            suffix = "% memory"

        lines = [title]

        for process in top_processes:
            lines.append(
                f"  PID {process['pid']} - "
                f"{process['name']} - "
                f"{process['value']:.1f}{suffix}"
            )

        return ToolResult(
            success=True,
            message="\n".join(lines),
            data=top_processes,
        )