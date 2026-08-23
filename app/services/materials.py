from __future__ import annotations

import json
from pathlib import Path

from mp_api.client import MPRester
import pymatgen

from figs import create_dp_figure as _create_dp_figure
from figs import create_structure_figure as _create_structure_figure
from figs import get_mp_structure as _get_mp_structure


ROOT_DIR = Path(__file__).resolve().parents[2]
STATIC_DIR = ROOT_DIR / "static"
STRUCTURE_DIR = STATIC_DIR / "assets" / "data" / "structures"
STRUCTURE_DIR.mkdir(parents=True, exist_ok=True)


def get_mp_structure(structure: str = "mp-81"):
    return _get_mp_structure(structure=structure)


def create_structure_figure(structure: str = "mp-81", zone_axis=None):
    if zone_axis is None:
        zone_axis = [1, 1, 1]
    return _create_structure_figure(structure=structure, zone_axis=zone_axis)


def create_dp_figure(structure: str = "mp-81", zone_axis=None, accelerating_voltage=200e3):
    if zone_axis is None:
        zone_axis = [1, 1, 1]
    return _create_dp_figure(
        structure=structure,
        zone_axis=zone_axis,
        accelerating_voltage=accelerating_voltage,
    )
