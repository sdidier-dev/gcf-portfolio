import os
from pprint import pprint
from datetime import timedelta, datetime

import numpy as np
from dash import dcc, html, Input, Output, State, callback, no_update, clientside_callback, Patch, ctx
import dash_mantine_components as dmc
import plotly.graph_objects as go
import plotly.io as pio
import plotly.express as px
from dash_iconify import DashIconify
from plotly.subplots import make_subplots

import pandas as pd

from app_config import df_FA, format_money_number_si, SECONDARY_COLOR, PRIMARY_COLOR

fig = go.Figure()

fig.add_histogram(
    x=df_FA['FA Financing'],
    marker=dict(
        color=PRIMARY_COLOR,
        line={'color': PRIMARY_COLOR, 'width': 2},
        # Trick to add transparency to the color marker only, not the border, as marker_opacity applies to both
        pattern={'fillmode': "replace", 'shape': "/", 'solidity': 1,
                 'fgcolor': PRIMARY_COLOR, 'fgopacity': 0.5}
    ),
    textfont_color='var(--mantine-color-text)', textangle=0,
    hovertemplate="<b>%{y}</b> Projects In The Range<br>"
                  "<b>[%{x}]</b><extra></extra>",
)

fig.update_xaxes(
    title={'text': 'Financing', 'font_size': 16, 'font_weight': "bold"},
    showgrid=False, showline=True, linewidth=2,
    ticks="outside", tickwidth=2, tickprefix='$'
)
fig.update_yaxes(
    title={'text': 'Projects Number', 'font_size': 16, 'font_weight': "bold"}, showgrid=False,
)

fig.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    showlegend=False,
    barcornerradius=5,  # radius of the corners of the bars
)

FA_histogram = dmc.Stack([
    dmc.Group([
        dmc.ButtonGroup([
            dmc.Button(
                "-", id='fa-histogram-minus-btn', variant="outline",
                color='Gray', fz=16, w=20, h=20, p=0,
                styles={"label": {'align-items': 'normal'}},
            ),
            dmc.Button(
                "+", id='fa-histogram-plus-btn', variant="outline",
                color='Gray', fz=16, w=20, h=20, p=0,
                styles={"label": {'align-items': 'normal'}},
            ),
        ], id='fa-histogram-grp-btn'),
        'Bins Size',
        dmc.Checkbox(id="fa-histogram-labels-chk", label="Show labels"),
    ], fz=14),
    dcc.Graph(
        id='fa-histogram-graph',
        config={'displayModeBar': False}, responsive=True,
        figure=fig,
        style={"flex": 1}
    ),
    # Note: we need to use a store to keep the nbinsx value (max bins) as it is not saved as param in fig
    dcc.Store(id='fa-histogram-nbinsx-store', data=19)
], p=10, style={"flex": 1})


@callback(
    Output('fa-histogram-graph', 'figure', allow_duplicate=True),
    Output('fa-histogram-nbinsx-store', 'data'),
    Input('fa-histogram-minus-btn', 'n_clicks'),
    Input('fa-histogram-plus-btn', 'n_clicks'),
    State('fa-histogram-nbinsx-store', 'data'),
    prevent_initial_call=True
)
def update_max_bins(_1, _2, nbinsx):
    # bins numbers to have nice splits
    bins_number_list = [2, 4, 8, 19, 38, 76, 188]

    current_index = bins_number_list.index(nbinsx)
    new_index = current_index + 1 if ctx.triggered_id == 'fa-histogram-minus-btn' else current_index - 1
    # check to stay inside the list
    if new_index < 0:
        new_index = 0
    elif new_index >= len(bins_number_list):
        new_index = len(bins_number_list) - 1

    new_nbinsx = bins_number_list[new_index]

    patched_fig = Patch()
    patched_fig["data"][0]['nbinsx'] = new_nbinsx
    return patched_fig, new_nbinsx


@callback(
    Output("fa-histogram-graph", "figure", allow_duplicate=True),
    Input("fa-grid", "virtualRowData"),
    prevent_initial_call=True
)
def update_x(virtual_data):
    patched_fig = Patch()
    if not virtual_data:
        patched_fig["data"][0]['x'] = None
        return patched_fig

    dff = pd.DataFrame(virtual_data)

    patched_fig["data"][0]['x'] = dff['FA Financing']
    return patched_fig


@callback(
    Output('fa-histogram-graph', 'figure', allow_duplicate=True),
    Input('fa-histogram-labels-chk', 'checked'),
    prevent_initial_call=True
)
def toggle_histogram_labels(checked):
    patched_fig = Patch()
    patched_fig["data"][0]['texttemplate'] = '%{y}' if checked else None
    return patched_fig


@callback(
    Output("fa-histogram-graph", "figure"),
    Input("color-scheme-switch", "checked"),
)
def update_figure_theme(checked):
    patched_fig = Patch()
    patched_fig["layout"]["template"] = pio.templates[f"mantine_{'light' if checked else 'dark'}"]
    return patched_fig
