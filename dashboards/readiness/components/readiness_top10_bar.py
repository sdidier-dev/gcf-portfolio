import os
from pprint import pprint

from dash import dcc, html, Input, Output, State, callback, no_update, clientside_callback, Patch, ctx
import dash_mantine_components as dmc
import plotly.graph_objects as go
import plotly.io as pio

import pandas as pd

from ..readiness_config import df_GCF_readiness

fig = go.Figure()
fig.add_bar(
    x=["2020-01-01", "2020-04-01", "2020-07-01"],
    y=[1000, 1500, 1700],
)

fig.update_layout(
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
)

readiness_top10_bar = dmc.Stack([
    dmc.Checkbox(id="readiness-top10-chk", label="Stacked", fz=16),
    dcc.Graph(
        id='readiness-top10-bar',
        config={'displayModeBar': False},
        responsive=True,
        figure=fig,
        style={"flex": 1}
    )
], p=10, style={"flex": 1})


@callback(
    Output("readiness-top10-bar", "figure"),
    Input("color-scheme-switch", "checked"),
)
def update_figure_theme(checked):
    patched_fig = Patch()
    patched_fig["layout"]["template"] = pio.templates[f"mantine_{'light' if checked else 'dark'}"]
    return patched_fig
