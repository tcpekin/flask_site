import io
import sys

import matplotlib.pyplot as plt
from flask import Flask, Response, render_template, request
from flask.helpers import redirect, url_for
from flask_flatpages import FlatPages, pygments_style_defs
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from figs import create_structure_figure, create_dp_figure

# from flask_frozen import Freezer

DEBUG = True
FLATPAGES_AUTO_RELOAD = DEBUG
FLATPAGES_EXTENSION = ".md"
FLATPAGES_ROOT = "content"
POST_DIR = "posts"


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
@app.route("/test/<structure>")
def test(structure=None):
    structure = structure
    # print(name)
    if request.args.get("structure") is not None and structure is None:
        try:
            structure = request.args.get("structure")
            success = True
        except:
            print("Stop trying to break the site.")
    if structure is not None:
        success = True
    else:
        success = False
    return render_template("test.html", success=success, structure=structure)


@app.route("/test/img/structure_plot.png")
def plot_structure_png():
    fig = create_structure_figure()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype="image/png")


@app.route("/test/img/dp_plot.png")
def plot_dp_png():
    fig = create_dp_figure()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype="image/png")


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
