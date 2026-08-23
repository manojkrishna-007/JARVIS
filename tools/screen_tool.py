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

        if action == "locate":
            target = kwargs.get("target", "")
            return self._locate_text(target)

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

    def _locate_text(self, target: str) -> ToolResult:
        """Find visible text and return its screen coordinates."""

        target = target.strip()

        if not target:
            return ToolResult(
                success=False,
                message="No text was provided to locate.",
            )

        try:
            image = ImageGrab.grab()

            ocr_data = pytesseract.image_to_data(
                image,
                output_type=pytesseract.Output.DICT,
            )

            target_words = target.lower().split()

            words = []

            for index, detected_text in enumerate(ocr_data["text"]):
                detected_text = detected_text.strip()

                if not detected_text:
                    continue

                words.append(
                    {
                        "text": detected_text,
                        "lower": detected_text.lower(),
                        "left": ocr_data["left"][index],
                        "top": ocr_data["top"][index],
                        "width": ocr_data["width"][index],
                        "height": ocr_data["height"][index],
                        "block": ocr_data["block_num"][index],
                        "par": ocr_data["par_num"][index],
                        "line": ocr_data["line_num"][index],
                    }
                )

            # Single-word target.
            if len(target_words) == 1:
                target_word = target_words[0]

                for word in words:
                    if target_word in word["lower"]:
                        return self._location_result(
                            target=target,
                            matched_words=[word],
                        )

            # Multi-word target.
            for start_index in range(len(words)):
                matched_words = []

                for offset, target_word in enumerate(target_words):
                    index = start_index + offset

                    if index >= len(words):
                        break

                    word = words[index]

                    # All words must belong to the same OCR line.
                    if matched_words:
                        previous = matched_words[-1]

                        if (
                            word["block"] != previous["block"]
                            or word["par"] != previous["par"]
                            or word["line"] != previous["line"]
                        ):
                            break

                    if target_word not in word["lower"]:
                        break

                    matched_words.append(word)

                if len(matched_words) == len(target_words):
                    return self._location_result(
                        target=target,
                        matched_words=matched_words,
                    )

            return ToolResult(
                success=False,
                message=f"Could not find '{target}' on the screen.",
            )

        except Exception as exc:
            return ToolResult(
                success=False,
                message=f"Text location failed: {exc}",
            )

    def _location_result(
        self,
        target: str,
        matched_words: list[dict],
    ) -> ToolResult:
        """Build a location result from one or more OCR words."""

        left = min(
            word["left"]
            for word in matched_words
        )

        top = min(
            word["top"]
            for word in matched_words
        )

        right = max(
            word["left"] + word["width"]
            for word in matched_words
        )

        bottom = max(
            word["top"] + word["height"]
            for word in matched_words
        )

        width = right - left
        height = bottom - top

        center_x = left + width // 2
        center_y = top + height // 2

        detected_text = " ".join(
            word["text"]
            for word in matched_words
        )

        return ToolResult(
            success=True,
            message=(
                f"Found '{target}' at "
                f"({center_x}, {center_y})."
            ),
            data={
                "target": target,
                "text": detected_text,
                "x": center_x,
                "y": center_y,
                "left": left,
                "top": top,
                "width": width,
                "height": height,
            },
        )