import os
import platform
import shutil

from tools.base import JarvisTool, ToolResult


class SystemTool(JarvisTool):
    """Provides basic information about the computer."""

    name = "system"
    description = "Provides information about the computer and operating system."

    def execute(self, **kwargs) -> ToolResult:
        """Return basic system information."""

        total, used, free = shutil.disk_usage("/")

        information = {
            "operating_system": platform.system(),
            "os_version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "cpu_count": os.cpu_count(),
            "disk_total_gb": round(total / (1024 ** 3), 2),
            "disk_used_gb": round(used / (1024 ** 3), 2),
            "disk_free_gb": round(free / (1024 ** 3), 2),
        }

        return ToolResult(
            success=True,
            message="System information retrieved.",
            data=information,
        )