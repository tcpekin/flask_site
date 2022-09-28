import numpy as np
import matplotlib
import warnings

matplotlib.use("svg")
import py4DSTEM

# from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

MP_API_KEY = "gSuVxl9wuF65iSH0DFGBkPNqzlqj60eD"

# surpress plt.show warnings because using non-interactive backend - can change py4DSTEM to not automatically plt.show things too?
warnings.filterwarnings("ignore", category=UserWarning)


def create_structure_figure(structure="mp-81", zone_axis=[1, 1, 1]):
    fig = Figure(dpi=200)
    axis = fig.add_subplot(1, 1, 1)
    crystal = py4DSTEM.process.diffraction.Crystal.from_pymatgen_structure(
        structure=structure,
        MP_key=MP_API_KEY,
    )
    fig, ax = crystal.plot_structure(returnfig=True, zone_axis_lattice=zone_axis, perspective_axes=True)
    ax.set_position([0, 0, 1, 1])
    return fig


def create_dp_figure(structure="mp-81", zone_axis=[1, 1, 1]):
    fig = Figure(dpi=100)
    ax = fig.add_subplot(1, 1, 1)
    crystal = py4DSTEM.process.diffraction.Crystal.from_pymatgen_structure(
        structure=structure,
        MP_key=MP_API_KEY,
    )
    crystal.calculate_structure_factors(1.5)
    crystal.setup_diffraction(accelerating_voltage=200e3)
    pattern = crystal.generate_diffraction_pattern(zone_axis_lattice=zone_axis)
    fig, ax = py4DSTEM.process.diffraction.crystal_viz.plot_diffraction_pattern(
        pattern, returnfig=True, figsize=(6, 6)
    )

    return fig
