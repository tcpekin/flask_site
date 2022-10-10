import io
import sys

import matplotlib.pyplot as plt
from flask import Flask, Response, render_template, render_template_string, request
from flask.helpers import redirect, url_for
from flask_flatpages import FlatPages, pygments_style_defs
from flask_flatpages.utils import pygmented_markdown

# from flask_frozen import Freezer

# from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.backends.backend_svg import FigureCanvasSVG as FigureCanvas
from matplotlib.figure import Figure

from figs import create_dp_figure, create_structure_figure


DEBUG = True
FLATPAGES_AUTO_RELOAD = DEBUG
FLATPAGES_EXTENSION = ".md"
FLATPAGES_ROOT = "content"
FLATPAGES_MARKDOWN_EXTENSIONS = ["codehilite", "fenced_code"]
POST_DIR = "posts"


def my_renderer(text):
    prerendered_body = render_template_string(text)
    print(prerendered_body)
    return pygmented_markdown(prerendered_body, flatpages=flatpages)


app = Flask(__name__)
flatpages = FlatPages(app)
# the following line must come after defining flatpages!
app.config["FLATPAGES_HTML_RENDERER"] = my_renderer
# freezer = Freezer(app)
app.config.from_object(__name__)


@app.route("/pygments.css")
def pygments_css():
    return pygments_style_defs("tango"), 200, {"Content-Type": "text/css"}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    content = flatpages.get_or_404("about")
    print("Hello world!")
    # content='1'
    return render_template("about.html", content=content)


# @app.route("/dp_sim/<structure>")
@app.route("/dp_sim/")
def dp_sim(structure=None, zone_axis=None):
    print(zone_axis)
    if request.args.get("structure") is not None and structure is None:
        try:
            structure = request.args.get("structure")
            success = True
        except:
            print("Stop trying to break the site.")
    if request.args.get("zone_axis") is not None and zone_axis is None:
        try:
            zone_axis = request.args.get("zone_axis")
            if len(zone_axis) == 3:
                zone_axis = [int(i) for i in zone_axis]
            else:
                zone_axis = [int(i) for i in zone_axis.split(",")]
                assert len(zone_axis) == 3
            success = True
        except:
            zone_axis = [1, 1, 1]
    else:
        zone_axis = [1, 1, 1]
    if structure is not None:
        success = True
    else:
        success = False

    h, k, l = zone_axis
    return render_template(
        "dp_sim.html", success=success, structure=structure, h=h, k=k, l=l
    )


@app.route("/dp_sim/img/<structure>_<h>_<k>_<l>_structure_plot.png")
def plot_structure_png(structure=None, h=None, k=None, l=None):
    zone_axis = [int(h), int(k), int(l)]
    fig = create_structure_figure(structure=structure, zone_axis=zone_axis)
    output = io.BytesIO()
    FigureCanvas(fig).print_svg(output)
    plt.close(fig)
    return Response(output.getvalue(), mimetype="image/svg+xml")


@app.route("/dp_sim/img/<structure>_<h>_<k>_<l>_dp_plot.png")
def plot_dp_png(structure=None, h=None, k=None, l=None):
    zone_axis = [int(h), int(k), int(l)]
    fig = create_dp_figure(structure=structure, zone_axis=zone_axis)
    output = io.BytesIO()
    FigureCanvas(fig).print_svg(output)
    plt.close(fig)
    return Response(output.getvalue(), mimetype="image/svg+xml")


@app.route("/posts/")
def posts():
    posts = [p for p in flatpages if p.path.startswith(POST_DIR)]
    # print(posts)
    posts.sort(key=lambda item: item["date"], reverse=True)
    return render_template("posts.html", posts=posts)


@app.route("/posts/<name>/")
def post(name):
    path = "{}/{}".format(POST_DIR, name)
    post = flatpages.get_or_404(path)
    return render_template("post.html", post=post)


@app.route("/tag/<string:tag>/")
def tag(tag):
    tagged = [p for p in flatpages if tag in p.meta.get("tags", [])]
    return render_template("tags.html", pages=tagged, tag=tag)


if __name__ == "__main__":
    # this only runs if we run python blog.py from the CLI, not flask --app run blog, as then __name__ is 'blog'
    # Both ways are supported but I think the latter is better. Debug stuff goes  then in CLI arguments or env variables.
    if len(sys.argv) > 1 and sys.argv[1] == "build":
        # freezer.freeze()
        pass
    else:
        app.run(host="0.0.0.0", debug=True)
