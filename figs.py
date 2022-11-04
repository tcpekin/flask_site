import numpy as np
import matplotlib
import warnings
import os
import json

matplotlib.use("svg")
import py4DSTEM
from mp_api.client import MPRester
import pymatgen

# from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

MP_API_KEY = os.environ.get("MP_API_KEY")

# surpress plt.show warnings because using non-interactive backend - can change py4DSTEM to not automatically plt.show things too?
warnings.filterwarnings("ignore", category=UserWarning)


def get_mp_structure(structure="mp-81"):
    """
    This will try to get the Materials Project structure and save it, if it does not already exist.
    """
    structure_path = f"static/assets/data/structures/{structure}.json"

    try:
        with open(structure_path, "r") as f:
            mp_structure = pymatgen.core.Structure.from_dict(json.load(f))
    except:
        with MPRester(MP_API_KEY) as mpr:
            mp_structure = mpr.get_structure_by_material_id(structure)
        with open(structure_path, "w") as f:
            json.dump(mp_structure.as_dict(), f)

    return mp_structure


def create_structure_figure(structure="mp-81", zone_axis=[1, 1, 1]):
    fig = Figure(dpi=200)
    axis = fig.add_subplot(1, 1, 1)
    structure = get_mp_structure(structure)
    crystal = py4DSTEM.process.diffraction.Crystal.from_pymatgen_structure(
        structure=structure,
    )
    fig, ax = crystal.plot_structure(
        returnfig=True, zone_axis_lattice=zone_axis, perspective_axes=True
    )
    ax.set_position([0, 0, 1, 1])
    return fig


def create_dp_figure(
    structure="mp-81", zone_axis=[1, 1, 1], accelerating_voltage=200e3
):
    fig = Figure(dpi=100)
    ax = fig.add_subplot(1, 1, 1)
    structure = get_mp_structure(structure)
    crystal = py4DSTEM.process.diffraction.Crystal.from_pymatgen_structure(
        structure=structure,
    )
    crystal.calculate_structure_factors(1.5)
    crystal.setup_diffraction(accelerating_voltage=accelerating_voltage)
    pattern = crystal.generate_diffraction_pattern(zone_axis_lattice=zone_axis)
    fig, ax = py4DSTEM.process.diffraction.crystal_viz.plot_diffraction_pattern(
        pattern, returnfig=True, figsize=(6, 6)
    )

    return fig
