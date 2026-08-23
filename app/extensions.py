from __future__ import annotations

from flask import render_template_string
from flask_flatpages import FlatPages, pygments_style_defs
from flask_flatpages.utils import pygmented_markdown


flatpages = FlatPages()


def my_renderer(text: str) -> str:
    prerendered_body = render_template_string(text)
    return pygmented_markdown(prerendered_body, flatpages=flatpages)


def pygments_css() -> tuple[str, int, dict[str, str]]:
    return pygments_style_defs("default"), 200, {"Content-Type": "text/css"}
