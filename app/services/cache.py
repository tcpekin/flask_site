from __future__ import annotations

import time
from pathlib import Path
from typing import Callable


def is_file_stale(path: Path, max_age_seconds: float) -> bool:
    try:
        return (time.time() - path.stat().st_mtime) > max_age_seconds
    except FileNotFoundError:
        return True


def ensure_file_with_cache(
    path: Path,
    fetcher: Callable[[], bytes],
    *,
    max_age_seconds: float,
) -> Path:
    if path.exists() and not is_file_stale(path, max_age_seconds):
        return path

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(fetcher())
    return path
