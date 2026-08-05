from pathlib import Path
import platform


class JarvisConfig:
    """Central configuration for the JARVIS runtime."""

    def __init__(self):
        self.name = "JARVIS"
        self.version = "0.1.0"

        self.project_root = Path(__file__).resolve().parent.parent
        self.data_dir = self.project_root / "data"
        self.logs_dir = self.project_root / "logs"

        self.data_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)

    @property
    def system_name(self) -> str:
        return platform.system()

    @property
    def python_version(self) -> str:
        return platform.python_version()

    def summary(self) -> str:
        return (
            f"Name: {self.name}\n"
            f"Version: {self.version}\n"
            f"Operating System: {self.system_name}\n"
            f"Python: {self.python_version}\n"
            f"Project Root: {self.project_root}"
        )