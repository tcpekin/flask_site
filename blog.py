import io
import sys
import os
import time
import requests
import logging
import pandas as pd
import numpy as np
import json
import plotly


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
fh = logging.FileHandler("./logs/ip_log.log", mode="a")
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)

logger.info("Log is working.")

import matplotlib.pyplot as plt
from flask import (
    Flask,
    Response,
    render_template,
    render_template_string,
    request,
    send_from_directory,
)
from flask.helpers import redirect, url_for
from flask_flatpages import FlatPages, pygments_style_defs
from flask_flatpages.utils import pygmented_markdown
from werkzeug.middleware.proxy_fix import ProxyFix
from xml.etree import ElementTree

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

from figs import create_dp_figure, create_structure_figure, get_mp_structure


DEBUG = bool(os.environ.get("FLASK_DEBUG", False))
FLATPAGES_AUTO_RELOAD = DEBUG
FLATPAGES_EXTENSION = ".md"
FLATPAGES_ROOT = "content"
FLATPAGES_MARKDOWN_EXTENSIONS = ["codehilite", "fenced_code"]
FLATPAGES_EXTENSION_CONFIGS = {"codehilite": {"linenums": "True"}}
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


@app.route("/pygments.css")
def pygments_css():
    return pygments_style_defs("default"), 200, {"Content-Type": "text/css"}


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


@app.route("/dp_sim/")
def dp_sim(structure=None, zone_axis=None):
    logger.info(f"{request.remote_addr} - {request.full_path} - {request.referrer}")
    print(zone_axis)
    message = ""
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
        try:
            get_mp_structure(structure=structure)
            success = True
        except Exception as e:
            message = str(e)
            success = False
    else:
        success = False

    h, k, l = zone_axis
    return render_template(
        "dp_sim.html",
        success=success,
        structure=structure,
        h=h,
        k=k,
        l=l,
        message=message,
    )


@app.route("/dp_sim/img/<structure>_<h>_<k>_<l>_structure_plot.png")
def plot_structure_png(structure=None, h=None, k=None, l=None):
    fname = f"assets/img/dps/{structure}_{h}_{k}_{l}_structure_plot.svg"
    folder = "static/"
    try:
        if os.path.isfile(folder + fname):
            with open(folder + fname) as f:
                # this parses the SVG XML, and if it has an error, forces a recomputation of the pattern.
                ElementTree.fromstring(f.read())
            return send_from_directory(folder, fname, mimetype="image/svg+xml")
        else:
            raise FileNotFoundError
    except:
        zone_axis = [int(h), int(k), int(l)]
        fig = create_structure_figure(structure=structure, zone_axis=zone_axis)
        output = io.BytesIO()
        fig.savefig(folder + fname)
        FigureCanvas(fig).print_svg(output)
        plt.close(fig)
        return Response(output.getvalue(), mimetype="image/svg+xml")


@app.route("/dp_sim/img/<structure>_<h>_<k>_<l>_dp_plot.png")
def plot_dp_png(structure=None, h=None, k=None, l=None):
    fname = f"assets/img/dps/{structure}_{h}_{k}_{l}_dp_plot.svg"
    folder = "static/"
    try:
        if os.path.isfile(folder + fname):
            with open(folder + fname) as f:
                ElementTree.fromstring(f.read())
            return send_from_directory(folder, fname, mimetype="image/svg+xml")
        else:
            raise FileNotFoundError
    except:
        zone_axis = [int(h), int(k), int(l)]
        fig = create_dp_figure(structure=structure, zone_axis=zone_axis)
        output = io.BytesIO()
        fig.savefig(folder + fname)
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


@app.route("/sine_graph/")
def sine_graph():
    import plotly.express as px

    x = np.linspace(0, 2 * np.pi, 100)
    y = np.sin(x) + np.random.normal(scale=0.3, size=100)
    fig = px.scatter(
        x=x,
        y=y,
    )
    fig.add_scatter(
        x=x,
        y=np.sin(x),
        mode="lines",
    )
    fig.update_layout(showlegend=False)
    fig["data"][1]["line"]["width"] = 5  # this is magic
    graphJSON = fig.to_json()
    return Response(graphJSON, mimetype="application/json")


@app.route("/covid_graph/")
def covid_graph():  # TODO - look into doing plotting in javascript instead

    data_path = os.path.join("static/assets/data", "fallzahlen_und_indikatoren.csv")
    try:
        file_age = time.time() - os.path.getmtime(data_path)
    except:
        file_age = 90000

    if file_age > 86400:
        print("Downloading data")
        url = "https://www.berlin.de/lageso/_assets/gesundheit/publikationen/corona/fallzahlen_und_indikatoren.csv"
        response = requests.get(url)
        with open(data_path, "wb") as f:
            f.write(response.content)
    else:
        print(
            f"Data has already been recently downloaded {file_age/86400:.3f} days ago."
        )

    data = pd.read_csv(data_path, sep=";", decimal=",")
    data["Datum"] = pd.to_datetime(data["Datum"], format="%d.%m.%Y")

    # import graph_objects from plotly package
    import plotly.graph_objects as go

    # import make_subplots function from plotly.subplots
    # to make grid of plots
    from plotly.subplots import make_subplots

    # use specs parameter in make_subplots function
    # to create secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # plot a scatter chart by specifying the x and y values
    # Use add_trace function to specify secondary_y axes.
    fig.add_trace(
        go.Scatter(
            x=data["Datum"], y=data["7-Tage-Inzidenz"], name="7 day incidence rate"
        ),
        secondary_y=False,
    )

    # Use add_trace function and specify secondary_y axes = True.
    fig.add_trace(
        go.Scatter(
            x=data["Datum"],
            y=data["7-Tage-Hosp-Inzidenz"],
            name="7 day hospital incidence rate",
        ),
        secondary_y=True,
    )

    # Adding title text to the figure and make over compare both lines
    fig.update_layout(title_text="Covid in Berlin", hovermode="x")

    # Naming x-axis
    fig.update_xaxes(title_text="Date")

    # Naming y-axes
    fig.update_yaxes(title_text="# of cases", secondary_y=False)
    fig.update_yaxes(title_text="# of hospitalizations ", secondary_y=True)
    fig.update_layout(
        legend=dict(orientation="h", yanchor="top", y=1.12, xanchor="left", x=0.01)
    )

    # graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON = fig.to_json()
    return Response(graphJSON, mimetype="application/json")


if __name__ == "__main__":
    # this only runs if we run python blog.py from the CLI, not flask --app run blog, as then __name__ is 'blog'
    # Both ways are supported but I think the latter is better. Debug stuff goes  then in CLI arguments or env variables.
    pass
