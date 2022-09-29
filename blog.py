import io
import sys

import matplotlib.pyplot as plt
from flask import Flask, Response, render_template, request
from flask.helpers import redirect, url_for
from flask_flatpages import FlatPages, pygments_style_defs

# from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.backends.backend_svg import FigureCanvasSVG as FigureCanvas
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


# @app.route("/test/<structure>")
@app.route("/test/")
def test(structure=None, zone_axis=None):
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
        "test.html", success=success, structure=structure, h=h, k=k, l=l
    )


@app.route("/test/img/<structure>_<h>_<k>_<l>_structure_plot.png")
def plot_structure_png(structure=None, h=None, k=None, l=None):
    zone_axis = [int(h), int(k), int(l)]
    fig = create_structure_figure(structure=structure, zone_axis=zone_axis)
    output = io.BytesIO()
    FigureCanvas(fig).print_svg(output)
    plt.close(fig)
    return Response(output.getvalue(), mimetype="image/svg+xml")


@app.route("/test/img/<structure>_<h>_<k>_<l>_dp_plot.png")
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
    print(posts)
    posts.sort(key=lambda item: item["date"], reverse=False)
    return render_template("posts.html", posts=posts)


@app.route("/posts/<name>/")
def post(name):
    path = "{}/{}".format(POST_DIR, name)
    print(path + "hkhk", file=sys.stderr)
    post = flatpages.get_or_404(path)
    return render_template("post.html", post=post)


if __name__ == "__main__":
    # this only runs if we run python blog.py from the CLI, not flask --app run blog, as then __name__ is 'blog'
    # Both ways are supported but I think the latter is better. Debug stuff goes  then in CLI arguments or env variables.
    if len(sys.argv) > 1 and sys.argv[1] == "build":
        # freezer.freeze()
        pass
    else:
        app.run(host="0.0.0.0", debug=True)
