import logging
from pathlib import Path


def create_logger(log_directory: Path) -> logging.Logger:
    """Create the main JARVIS logger."""

    logger = logging.getLogger("JARVIS")
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    log_file = log_directory / "jarvis.log"

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    file_handler = logging.FileHandler(
        log_file,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger