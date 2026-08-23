from __future__ import annotations

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]


class Config:
    BASE_DIR = BASE_DIR
    ROOT_DIR = BASE_DIR
    STATIC_FOLDER = str(BASE_DIR / "static")
    TEMPLATES_FOLDER = str(BASE_DIR / "templates")
    DEBUG = os.environ.get("FLASK_DEBUG", "").lower() in {"1", "true", "yes", "on"}
    FLATPAGES_AUTO_RELOAD = DEBUG
    FLATPAGES_EXTENSION = ".md"
    FLATPAGES_ROOT = str(BASE_DIR / "content")
    FLATPAGES_MARKDOWN_EXTENSIONS = ["codehilite", "fenced_code"]
    FLATPAGES_EXTENSION_CONFIGS = {"codehilite": {"linenums": "True"}}
    POST_DIR = "posts"
