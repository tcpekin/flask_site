from __future__ import annotations

from flask import Blueprint, render_template, request

from app.extensions import flatpages


site_bp = Blueprint("site", __name__)


@site_bp.route("/")
def index():
    return render_template("index.html")


@site_bp.route("/about")
def about():
    content = flatpages.get_or_404("about")
    return render_template("about.html", content=content)


@site_bp.route("/posts/")
def posts():
    items = [page for page in flatpages if page.path.startswith("posts")]
    items.sort(key=lambda item: item["date"], reverse=True)
    return render_template("posts.html", posts=items)


@site_bp.route("/posts/<name>/")
def post(name):
    path = f"posts/{name}"
    page = flatpages.get_or_404(path)
    return render_template("post.html", post=page)


@site_bp.route("/tag/<string:tag>/")
def tag(tag):
    tagged = [page for page in flatpages if tag in page.meta.get("tags", [])]
    return render_template("tags.html", pages=tagged, tag=tag)
