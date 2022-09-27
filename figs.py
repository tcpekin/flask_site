import numpy as np
import matplotlib

matplotlib.use("Agg")
import py4DSTEM
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

MP_API_KEY = "gSuVxl9wuF65iSH0DFGBkPNqzlqj60eD"


def create_structure_figure(structure="mp-81"):
    fig = Figure(dpi=200)
    axis = fig.add_subplot(1, 1, 1)
    crystal = py4DSTEM.process.diffraction.Crystal.from_pymatgen_structure(
        structure=structure,
        MP_key=MP_API_KEY,
    )
    fig, ax = crystal.plot_structure(returnfig=True, zone_axis_lattice=(1, 1, 1))
    # xs = range(100)
    # ys = [np.random.randint(1, 50) for x in xs]
    # axis.plot(xs, ys)
    ax.set_position([0,0,1,1])
    return fig


def create_dp_figure(structure="mp-81"):
    fig = Figure(dpi=100)
    ax = fig.add_subplot(1, 1, 1)
    crystal = py4DSTEM.process.diffraction.Crystal.from_pymatgen_structure(
        structure=structure,
        MP_key=MP_API_KEY,
    )
    crystal.calculate_structure_factors(1.5)
    crystal.setup_diffraction(accelerating_voltage=200e3)
    pattern = crystal.generate_diffraction_pattern(zone_axis_lattice=(1, 1, 1))
    fig, ax = py4DSTEM.process.diffraction.crystal_viz.plot_diffraction_pattern(
        pattern, returnfig=True, figsize=(6,6)
    )
    # fig.tight_layout()
    # ax.set_position([0.05,0.05,.95,.95])

    return fig
