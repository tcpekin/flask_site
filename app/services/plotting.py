from __future__ import annotations

import base64
import json
import math

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def _decode_plotly_json(value):
    if isinstance(value, np.ndarray):
        return _decode_plotly_json(value.tolist())
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, float):
        if not math.isfinite(value):
            return None
        return value
    if isinstance(value, dict):
        if {"dtype", "bdata"}.issubset(value.keys()):
            dtype = value["dtype"]
            payload = base64.b64decode(value["bdata"])
            return _decode_plotly_json(np.frombuffer(payload, dtype=np.dtype(dtype)).tolist())
        return {key: _decode_plotly_json(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_decode_plotly_json(item) for item in value]
    if isinstance(value, tuple):
        return [_decode_plotly_json(item) for item in value]
    return value


def _plotly_figure_json(fig):
    return json.dumps(_decode_plotly_json(fig.to_dict()), allow_nan=False)


def build_sine_figure():
    x = np.linspace(0, 2 * np.pi, 100)
    y = np.sin(x) + np.random.normal(scale=0.3, size=100)
    fig = px.scatter(x=x, y=y)
    fig.add_scatter(x=x, y=np.sin(x), mode="lines")
    fig.update_layout(showlegend=False)
    fig["data"][1]["line"]["width"] = 5
    return fig


def build_covid_figure(data: pd.DataFrame):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(x=data["Datum"], y=data["7-Tage-Inzidenz"], name="7 day incidence rate"),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=data["Datum"], y=data["7-Tage-Hosp-Inzidenz"], name="7 day hospital incidence rate"),
        secondary_y=True,
    )
    fig.update_layout(title_text="Covid in Berlin", hovermode="x")
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="# of cases", secondary_y=False)
    fig.update_yaxes(title_text="# of hospitalizations ", secondary_y=True)
    fig.update_layout(legend=dict(orientation="h", yanchor="top", y=1.12, xanchor="left", x=0.01))
    return fig
