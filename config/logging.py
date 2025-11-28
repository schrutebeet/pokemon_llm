import logging
import os
from pathlib import Path
from typing import Optional


logger = logging.getLogger("pokemon_llm")

def _ensure_dir_for(path: Path) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

def _add_file_handler(path: Path, level: int) -> None:
    _ensure_dir_for(path)
    fh = logging.FileHandler(path, encoding="utf-8")
    fh.setLevel(level)
    fh.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    logger.addHandler(fh)

def _add_stream_handler(level: int) -> None:
    sh = logging.StreamHandler()
    sh.setLevel(level)
    sh.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    logger.addHandler(sh)

def configure(log_file_path: Optional[str] = None, level: int = logging.DEBUG) -> None:
    """
    Configure the module-level `logger`.

    - log_file_path: path to .txt file to write logs. If None, uses POKEMON_LOG_PATH env var
      or defaults to './logs/pokemon_log.txt'.
    - level: logging level (e.g. logging.DEBUG, logging.INFO).
    """
    if logger.handlers:
        # Already configured; avoid adding duplicate handlers
        return

    if log_file_path is None:
        log_file_path = os.environ.get("POKEMON_LOG_PATH", "./logs/pokemon_log.txt")

    logger.setLevel(level)
    _add_stream_handler(level)

    try:
        _add_file_handler(Path(log_file_path), level)
    except Exception:
        # If file handler can't be created, still allow console logging
        pass

def set_log_file(path: str, level: int = logging.INFO) -> None:
    """
    Replace any existing FileHandler(s) with one that writes to `path`.
    Useful to change the log file at runtime.
    """
    # remove existing file handlers
    for h in list(logger.handlers):
        if isinstance(h, logging.FileHandler):
            logger.removeHandler(h)
            try:
                h.close()
            except Exception:
                pass

    try:
        _add_file_handler(Path(path), level)
    except Exception:
        pass

# Auto-configure on import with defaults so callers can immediately do:
#   from config.logging import logger
#   logger.warning("Something something")
configure(level = logging.INFO)
