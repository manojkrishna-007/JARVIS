from pathlib import Path
from datetime import datetime

from PIL import ImageGrab
import pytesseract

from tools.base import JarvisTool, ToolResult


class ScreenTool(JarvisTool):
    """Captures and inspects the user's screen."""

    name = "screen"
    description = "Captures screenshots and provides screen information."

    def execute(
        self,
        action: str = "",
        path: str = "",
        **kwargs,
    ) -> ToolResult:
        """Execute a screen operation."""

        action = action.strip().lower()

        if action == "screenshot":
            return self._screenshot(path)

        if action == "size":
            return self._screen_size()
        
        if action == "read":
            return self._read_screen()

        return ToolResult(
            success=False,
            message=f"Unknown screen action: {action}",
        )

    def _screenshot(self, path: str = "") -> ToolResult:
        """Capture the current screen."""

        try:
            if not path:
                timestamp = datetime.now().strftime(
                    "%Y%m%d_%H%M%S"
                )

                path = (
                    Path.cwd()
                    / "data"
                    / "screenshots"
                    / f"screen_{timestamp}.png"
                )

            output_path = Path(path)
            output_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            image = ImageGrab.grab()

            image.save(output_path)

            return ToolResult(
                success=True,
                message=f"Screenshot saved to {output_path}",
                data={
                    "path": str(output_path),
                    "width": image.width,
                    "height": image.height,
                },
            )

        except Exception as exc:
            return ToolResult(
                success=False,
                message=f"Screenshot failed: {exc}",
            )

    def _screen_size(self) -> ToolResult:
        """Return the current screen dimensions."""

        try:
            image = ImageGrab.grab()

            return ToolResult(
                success=True,
                message=(
                    f"Screen size: "
                    f"{image.width}x{image.height}"
                ),
                data={
                    "width": image.width,
                    "height": image.height,
                },
            )

        except Exception as exc:
            return ToolResult(
                success=False,
                message=f"Could not determine screen size: {exc}",
            )        
        
    def _read_screen(self) -> ToolResult:
        """Capture the screen and extract visible text using OCR."""

        try:
            image = ImageGrab.grab()

            text = pytesseract.image_to_string(image).strip()

            if not text:
                return ToolResult(
                    success=True,
                    message="I couldn't detect any readable text on the screen.",
                    data={
                        "text": "",
                    },
                )

            return ToolResult(
                success=True,
                message=f"Text detected on screen:\n\n{text}",
                data={
                    "text": text,
                },
            )

        except Exception as exc:
            return ToolResult(
                success=False,
                message=f"Screen OCR failed: {exc}",
            )