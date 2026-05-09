import logging
import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler

from rich.logging import RichHandler
from rich.console import Console

from app.config import settings

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

console = Console()


class JSONFormatter(logging.Formatter):
    """Formats log records as JSON lines for file output."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            log_obj["exc"] = self.formatException(record.exc_info)
        # Attach any extra fields
        for key, val in record.__dict__.items():
            if key not in {
                "msg", "args", "levelname", "levelno", "pathname", "filename",
                "module", "exc_info", "exc_text", "stack_info", "lineno",
                "funcName", "created", "msecs", "relativeCreated", "thread",
                "threadName", "processName", "process", "name", "message",
            }:
                log_obj[key] = val
        return json.dumps(log_obj)


def _build_handlers() -> list[logging.Handler]:
    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Terminal: rich colored
    rich_handler = RichHandler(
        console=console,
        rich_tracebacks=True,
        show_path=False,
        markup=True,
    )
    rich_handler.setLevel(level)

    # All events → JSONL rotating file
    app_file = RotatingFileHandler(
        LOG_DIR / "app.jsonl", maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    app_file.setFormatter(JSONFormatter())
    app_file.setLevel(level)

    # Errors only → plain text file
    error_file = RotatingFileHandler(
        LOG_DIR / "errors.log", maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    error_file.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    error_file.setLevel(logging.ERROR)

    return [rich_handler, app_file, error_file]


def _configure_root() -> None:
    root = logging.getLogger()
    if root.handlers:
        return  # already configured
    root.setLevel(logging.DEBUG)
    for h in _build_handlers():
        root.addHandler(h)
    # Silence noisy third-party loggers
    for noisy in ("httpx", "httpcore", "urllib3", "sentence_transformers"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


_configure_root()


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
