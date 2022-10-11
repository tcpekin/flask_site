import io
import sys
import os
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
fh = logging.FileHandler("./logs/ip_log.log", mode="a")
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)

logger.info("Log is working.")

import matplotlib.pyplot as plt
from flask import Flask, Response, render_template, render_template_string, request
from flask.helpers import redirect, url_for
from flask_flatpages import FlatPages, pygments_style_defs
from flask_flatpages.utils import pygmented_markdown
from werkzeug.middleware.proxy_fix import ProxyFix

# from flask_frozen import Freezer

# from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.backends.backend_svg import FigureCanvasSVG as FigureCanvas
from matplotlib.figure import Figure

# load our environment variables - only necessary for when we want to run 
# gunicorn by itself, otherwise we can specify the .env file in the Docker 
# compose file and it takes care of it for us. When we use `flask run`, it also 
# automatically loads environment variables from both .env and .flaskenv
from dotenv import load_dotenv
load_dotenv()

from figs import create_dp_figure, create_structure_figure


DEBUG = bool(os.environ.get("FLASK_DEBUG", False))
FLATPAGES_AUTO_RELOAD = DEBUG
FLATPAGES_EXTENSION = ".md"
FLATPAGES_ROOT = "content"
FLATPAGES_MARKDOWN_EXTENSIONS = ["codehilite", "fenced_code"]
POST_DIR = "posts"


def my_renderer(text):
    prerendered_body = render_template_string(text)
    return pygmented_markdown(prerendered_body, flatpages=flatpages)


app = Flask(__name__)
flatpages = FlatPages(app)
# the following line must come after defining flatpages otherwise code blocks do not render properly!
app.config["FLATPAGES_HTML_RENDERER"] = my_renderer
# freezer = Freezer(app)
app.config.from_object(__name__)
# should double check the following line to make sure that the correct number of proxies are set
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=0)

# these can be uncommented in development to see what is going on in your app more easily
if DEBUG is True:
    from flask_debugtoolbar import DebugToolbarExtension
    app.config['SECRET_KEY'] = 'ASDF'
    toolbar = DebugToolbarExtension(app)


@app.route("/pygments.css")
def pygments_css():
    return pygments_style_defs("tango"), 200, {"Content-Type": "text/css"}


@app.route("/")
def index():
    logger.info(f"{request.remote_addr} - {request.full_path} - {request.referrer}")
    return render_template("index.html")


@app.route("/about")
def about():
    logger.info(f"{request.remote_addr} - {request.full_path} - {request.referrer}")
    content = flatpages.get_or_404("about")
    print("Hello visitor!")
    return render_template("about.html", content=content)


# @app.route("/dp_sim/<structure>")
@app.route("/dp_sim/")
def dp_sim(structure=None, zone_axis=None):
    logger.info(f"{request.remote_addr} - {request.full_path} - {request.referrer}")
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
    logger.info(f"{request.remote_addr} - {request.full_path} - {request.referrer}")
    posts = [p for p in flatpages if p.path.startswith(POST_DIR)]
    # print(posts)
    posts.sort(key=lambda item: item["date"], reverse=True)
    return render_template("posts.html", posts=posts)


@app.route("/posts/<name>/")
def post(name):
    logger.info(f"{request.remote_addr} - {request.full_path} - {request.referrer}")
    path = "{}/{}".format(POST_DIR, name)
    post = flatpages.get_or_404(path)
    return render_template("post.html", post=post)


@app.route("/tag/<string:tag>/")
def tag(tag):
    logger.info(f"{request.remote_addr} - {request.full_path} - {request.referrer}")
    tagged = [p for p in flatpages if tag in p.meta.get("tags", [])]
    return render_template("tags.html", pages=tagged, tag=tag)


if __name__ == "__main__":
    # this only runs if we run python blog.py from the CLI, not flask --app run blog, as then __name__ is 'blog'
    # Both ways are supported but I think the latter is better. Debug stuff goes  then in CLI arguments or env variables.
    pass
