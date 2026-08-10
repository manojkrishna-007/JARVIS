import subprocess

from tools.base import JarvisTool, ToolResult


class AppTool(JarvisTool):
    """Launches approved applications on Windows."""

    name = "app"
    description = "Launches applications installed on the computer."

    APPLICATIONS = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "paint": "mspaint.exe",
        "explorer": "explorer.exe",
        "file explorer": "explorer.exe",
    }

    def execute(self, application: str = "", **kwargs) -> ToolResult:
        """Launch an approved application and return its PID."""

        application = application.strip().lower()

        if not application:
            return ToolResult(
                success=False,
                message="No application was specified.",
            )

        executable = self.APPLICATIONS.get(application)

        if executable is None:
            return ToolResult(
                success=False,
                message=(
                    f"I don't have '{application}' in my approved "
                    "application list yet."
                ),
            )

        try:
            process = subprocess.Popen(
                executable,
                shell=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            return ToolResult(
                success=True,
                message=f"Opening {application}.",
                data={
                    "application": application,
                    "executable": executable,
                    "pid": process.pid,
                },
            )

        except FileNotFoundError:
            return ToolResult(
                success=False,
                message=f"I couldn't find {application} on this computer.",
            )

        except OSError as exc:
            return ToolResult(
                success=False,
                message=f"Windows could not launch {application}: {exc}",
            )