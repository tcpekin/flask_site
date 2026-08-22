import json
import os
from pathlib import Path

import matplotlib
import numpy as np
import py4DSTEM
import pymatgen
from mp_api.client import MPRester

matplotlib.use("svg")
from matplotlib.figure import Figure


ROOT_DIR = Path(__file__).resolve().parent
STATIC_DIR = ROOT_DIR / "static"
STRUCTURE_DIR = STATIC_DIR / "assets" / "data" / "structures"
STRUCTURE_DIR.mkdir(parents=True, exist_ok=True)
MP_API_KEY = os.environ.get("MP_API_KEY")


def get_mp_structure(structure="mp-81"):
    """Return a Materials Project structure, caching it under static/assets/data/structures."""
    structure_path = STRUCTURE_DIR / f"{structure}.json"

    try:
        with structure_path.open("r", encoding="utf-8") as handle:
            return pymatgen.core.Structure.from_dict(json.load(handle))
    except FileNotFoundError:
        with MPRester(MP_API_KEY) as mpr:
            mp_structure = mpr.get_structure_by_material_id(structure)

        if isinstance(mp_structure, list):
            raise ValueError(
                f"Crystal {structure} is not in the Materials Project database, please choose a valid input."
            )

        with structure_path.open("w", encoding="utf-8") as handle:
            json.dump(mp_structure.as_dict(), handle)
        return mp_structure


def create_structure_figure(structure="mp-81", zone_axis=None):
    if zone_axis is None:
        zone_axis = [1, 1, 1]

    fig = Figure(dpi=200)
    fig.add_subplot(1, 1, 1)
    structure = get_mp_structure(structure)
    crystal = py4DSTEM.process.diffraction.Crystal.from_pymatgen_structure(
        structure=structure,
    )
    fig, ax = crystal.plot_structure(
        returnfig=True, zone_axis_lattice=zone_axis, perspective_axes=True
    )
    ax.set_position([0, 0, 1, 1])
    return fig


def create_dp_figure(structure="mp-81", zone_axis=None, accelerating_voltage=200e3):
    if zone_axis is None:
        zone_axis = [1, 1, 1]

    fig = Figure(dpi=100)
    fig.add_subplot(1, 1, 1)
    structure = get_mp_structure(structure)
    crystal = py4DSTEM.process.diffraction.Crystal.from_pymatgen_structure(
        structure=structure,
    )
    crystal.calculate_structure_factors(1.5)
    crystal.setup_diffraction(accelerating_voltage=accelerating_voltage)
    pattern = crystal.generate_diffraction_pattern(zone_axis_lattice=zone_axis)
    fig, _ = py4DSTEM.process.diffraction.crystal_viz.plot_diffraction_pattern(
        pattern, returnfig=True, figsize=(6, 6)
    )
    return fig
