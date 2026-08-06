import os
import subprocess
from pathlib import Path

from tools.base import JarvisTool, ToolResult


class FileTool(JarvisTool):
    """Handles safe file and folder operations."""

    name = "files"
    description = "Creates, opens, reads, and checks files and folders."

    def execute(
        self,
        action: str = "",
        path: str = "",
        content: str = "",
        **kwargs,
    ) -> ToolResult:
        """Execute a file operation."""

        action = action.strip().lower()
        path = path.strip()

        if not action:
            return ToolResult(
                success=False,
                message="No file action was specified.",
            )

        if not path:
            return ToolResult(
                success=False,
                message="No file or folder path was specified.",
            )

        try:
            target = Path(path).expanduser().resolve()

            if action == "create_folder":
                target.mkdir(parents=True, exist_ok=True)

                return ToolResult(
                    success=True,
                    message=f"Folder created: {target}",
                    data={"path": str(target)},
                )

            if action == "create_file":
                target.parent.mkdir(parents=True, exist_ok=True)

                if target.exists():
                    return ToolResult(
                        success=False,
                        message=f"File already exists: {target}",
                    )

                target.write_text(
                    content,
                    encoding="utf-8",
                )

                return ToolResult(
                    success=True,
                    message=f"File created: {target}",
                    data={"path": str(target)},
                )

            if action == "exists":
                exists = target.exists()

                return ToolResult(
                    success=True,
                    message=(
                        f"{'Exists' if exists else 'Does not exist'}: "
                        f"{target}"
                    ),
                    data={
                        "path": str(target),
                        "exists": exists,
                    },
                )

            if action == "read_file":
                if not target.exists():
                    return ToolResult(
                        success=False,
                        message=f"File does not exist: {target}",
                    )

                if not target.is_file():
                    return ToolResult(
                        success=False,
                        message=f"That path is not a file: {target}",
                    )

                text = target.read_text(encoding="utf-8")

                return ToolResult(
                    success=True,
                    message=text,
                    data={
                        "path": str(target),
                        "content": text,
                    },
                )

            if action == "open":
                if not target.exists():
                    return ToolResult(
                        success=False,
                        message=f"Path does not exist: {target}",
                    )

                os.startfile(str(target))

                return ToolResult(
                    success=True,
                    message=f"Opened: {target}",
                )

            return ToolResult(
                success=False,
                message=f"Unknown file action: {action}",
            )

        except PermissionError:
            return ToolResult(
                success=False,
                message=f"Permission denied: {target}",
            )

        except OSError as exc:
            return ToolResult(
                success=False,
                message=f"File operation failed: {exc}",
            )