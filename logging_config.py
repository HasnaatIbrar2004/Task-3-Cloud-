"""Central logging setup.

Everything (the app's own logs *and* uvicorn's server/access logs) is written to
``<log_dir>/logs.log`` (default: ``logs/logs.log`` in the project root) and also
echoed to the console so ``docker compose logs`` works.

Minimum level is INFO (configurable with LOG_LEVEL, but never below INFO).
Never log passwords, MFA codes or tokens.
"""
import logging
import logging.config
from pathlib import Path

from config import get_settings

BASE_DIR = Path(__file__).resolve().parent
LOG_FILE_NAME = "logs.log"
FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"

_ALLOWED = {"INFO", "WARNING", "ERROR", "CRITICAL"}


def _resolve_log_file(log_dir: str) -> Path:
    path = Path(log_dir)
    if not path.is_absolute():
        path = BASE_DIR / path
    path.mkdir(parents=True, exist_ok=True)
    return path / LOG_FILE_NAME


def setup_logging() -> Path:
    s = get_settings()
    level = s.log_level.upper() if s.log_level.upper() in _ALLOWED else "INFO"
    log_file = _resolve_log_file(s.log_dir)

    handlers = {
        "console": {"class": "logging.StreamHandler", "formatter": "std"},
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "std",
            "filename": str(log_file),
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 3,
            "encoding": "utf-8",
        },
    }
    both = ["console", "file"]
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {"std": {"format": FORMAT}},
            "handlers": handlers,
            "root": {"level": level, "handlers": both},
            # uvicorn installs its own handlers and does not propagate, so wire it up explicitly
            "loggers": {
                name: {"level": level, "handlers": both, "propagate": False}
                for name in ("uvicorn", "uvicorn.error", "uvicorn.access")
            },
        }
    )
    # The dev auto-reloader logs every file change; if that goes into logs.log it
    # counts as a new change and causes an endless reload loop.
    logging.getLogger("watchfiles").setLevel(logging.WARNING)
    logging.getLogger(__name__).info("Logging to %s (level %s)", log_file, level)
    return log_file
