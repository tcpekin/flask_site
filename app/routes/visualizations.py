from __future__ import annotations

import io
import os
import time
from pathlib import Path
from xml.etree import ElementTree

from flask import Blueprint, Response, current_app, render_template, request, send_from_directory

from app.services.data_loaders import load_covid_dataframe
from app.services.materials import create_dp_figure, create_structure_figure, get_mp_structure
from app.services.plotting import _plotly_figure_json, build_covid_figure, build_sine_figure


visualizations_bp = Blueprint("visualizations", __name__)


@visualizations_bp.route("/pygments.css")
def pygments_css():
    from flask_flatpages import pygments_style_defs

    return pygments_style_defs("default"), 200, {"Content-Type": "text/css"}


@visualizations_bp.route("/dp_sim/")
def dp_sim(structure=None, zone_axis=None):
    message = ""
    success = False

    if request.args.get("structure") is not None and structure is None:
        structure = request.args.get("structure")
        success = True

    if request.args.get("zone_axis") is not None and zone_axis is None:
        raw_zone_axis = request.args.get("zone_axis")
        try:
            if len(raw_zone_axis) == 3:
                zone_axis = [int(i) for i in raw_zone_axis]
            else:
                zone_axis = [int(i) for i in raw_zone_axis.split(",")]
                assert len(zone_axis) == 3
            success = True
        except Exception:
            zone_axis = [1, 1, 1]
    else:
        zone_axis = [1, 1, 1]

    if structure is not None:
        try:
            get_mp_structure(structure=structure)
            success = True
        except Exception as exc:  # pragma: no cover - defensive validation path
            message = str(exc)
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


@visualizations_bp.route("/dp_sim/img/<structure>_<h>_<k>_<l>_structure_plot.png")
def plot_structure_png(structure=None, h=None, k=None, l=None):
    static_root = Path(current_app.root_path).resolve().parent / "static"
    file_name = f"assets/img/dps/{structure}_{h}_{k}_{l}_structure_plot.svg"
    file_path = static_root / file_name

    try:
        if file_path.is_file():
            with file_path.open("r", encoding="utf-8") as handle:
                ElementTree.fromstring(handle.read())
            return send_from_directory(str(static_root), file_name, mimetype="image/svg+xml")
        raise FileNotFoundError
    except (FileNotFoundError, ElementTree.ParseError):
        zone_axis = [int(h), int(k), int(l)]
        fig = create_structure_figure(structure=structure, zone_axis=zone_axis)
        output = io.BytesIO()
        file_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(str(file_path))
        fig.savefig(str(file_path.with_suffix(".svg")))
        FigureCanvas = __import__("matplotlib.backends.backend_svg", fromlist=["FigureCanvasSVG"]).FigureCanvasSVG
        FigureCanvas(fig).print_svg(output)
        import matplotlib.pyplot as plt

        plt.close(fig)
        return Response(output.getvalue(), mimetype="image/svg+xml")


@visualizations_bp.route("/dp_sim/img/<structure>_<h>_<k>_<l>_dp_plot.png")
def plot_dp_png(structure=None, h=None, k=None, l=None):
    static_root = Path(current_app.root_path).resolve().parent / "static"
    file_name = f"assets/img/dps/{structure}_{h}_{k}_{l}_dp_plot.svg"
    file_path = static_root / file_name

    try:
        if file_path.is_file():
            with file_path.open("r", encoding="utf-8") as handle:
                ElementTree.fromstring(handle.read())
            return send_from_directory(str(static_root), file_name, mimetype="image/svg+xml")
        raise FileNotFoundError
    except (FileNotFoundError, ElementTree.ParseError):
        zone_axis = [int(h), int(k), int(l)]
        fig = create_dp_figure(structure=structure, zone_axis=zone_axis)
        output = io.BytesIO()
        file_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(str(file_path))
        FigureCanvas = __import__("matplotlib.backends.backend_svg", fromlist=["FigureCanvasSVG"]).FigureCanvasSVG
        FigureCanvas(fig).print_svg(output)
        import matplotlib.pyplot as plt

        plt.close(fig)
        return Response(output.getvalue(), mimetype="image/svg+xml")


@visualizations_bp.route("/sine_graph/")
def sine_graph():
    fig = build_sine_figure()
    return Response(_plotly_figure_json(fig), mimetype="application/json")


@visualizations_bp.route("/covid_graph/")
def covid_graph():
    data = load_covid_dataframe(current_app.root_path, max_age_seconds=86400)
    fig = build_covid_figure(data)
    return Response(_plotly_figure_json(fig), mimetype="application/json")
