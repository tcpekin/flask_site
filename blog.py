import sys
from flask import Flask, render_template, request
from flask.helpers import redirect, url_for
from flask_flatpages import FlatPages, pygments_style_defs

import py4DSTEM
import numpy as np
import matplotlib.pyplot as plt

# from flask_frozen import Freezer

DEBUG = True
FLATPAGES_AUTO_RELOAD = DEBUG
FLATPAGES_EXTENSION = ".md"
FLATPAGES_ROOT = "content"
POST_DIR = "posts"

MP_API_KEY='gSuVxl9wuF65iSH0DFGBkPNqzlqj60eD'

app = Flask(__name__)
flatpages = FlatPages(app)
# freezer = Freezer(app)
app.config.from_object(__name__)


@app.route("/")
def index():

    return render_template("index.html")


@app.route("/about")
def about():
    content = flatpages.get_or_404("about")
    print("Hello world!")
    # content='1'
    return render_template("about.html", content=content)


@app.route("/test/")
@app.route('/test/<structure>')
def test(structure=None):
    name = structure
    print(name)
    if request.args.get('name') is not None and name is None:
        try:
            structure = request.args.get('name')
            success = True
            print(name)
        except:
            print("Stop trying to break the site.")
    if name is not None: success=True
    return render_template("test.html", success=success, name=structure)


@app.route("/posts/")
def posts():
    posts = [p for p in flatpages if p.path.startswith(POST_DIR)]
    posts.sort(key=lambda item: item["date"], reverse=False)
    return render_template("posts.html", posts=posts)


@app.route("/posts/<name>/")
def post(name):
    path = "{}/{}".format(POST_DIR, name)
    print(path + "hkhk", file=sys.stderr)
    post = flatpages.get_or_404(path)
    return render_template("post.html", post=post)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "build":
        # freezer.freeze()
        pass
    else:
        app.run(host="0.0.0.0", debug=True)
