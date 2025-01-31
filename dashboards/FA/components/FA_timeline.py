import os
from pprint import pprint
from datetime import timedelta, datetime

import numpy as np
from dash import dcc, html, Input, Output, State, callback, no_update, clientside_callback, Patch, ctx
import dash_mantine_components as dmc
import plotly.graph_objects as go
import plotly.io as pio
import plotly.express as px

import pandas as pd

from app_config import df_FA, PRIMARY_COLOR, SECONDARY_COLOR

# dff = df_FA.groupby(['BM', 'Theme'])['FA Financing'].agg('sum').reset_index()
# dff = df_FA.groupby(['BM', 'Theme']).agg({'FA Financing': 'sum'}).reset_index()

# sum  financing by board meeting and theme
dff = df_FA.groupby(['Theme', 'BM'])['FA Financing'].sum().reset_index()
# get the full range of board meeting numbers as int that fill be used for x axis
dff['BM'] = dff['BM'].apply(lambda i: int(i.replace('B.', '')))
boards = pd.Series(range(dff['BM'].min(), dff['BM'].max() + 1), name='BM')

colors = {
    'Adaptation': '#15a14a',
    'Cross-cutting': '#0E7065',
    'Mitigation': '#084081',
}

fig = go.Figure()

y_annotation_cumul = 0  # used to position the annotations for the last values
for cat in dff['Theme'].unique():
    # merge with Board series to add the missing boards for that cat, add ) for missing board and
    # sort by BM to be sure there are ordered for the cumulated sum
    df_cat = pd.merge(boards, dff[dff['Theme'] == cat], on='BM', how='left').fillna(value=0).sort_values('BM')
    df_cat['cumsum'] = df_cat['FA Financing'].cumsum()

    fig.add_scatter(
        name=cat,
        mode='lines+markers+text',
        x=df_cat['BM'],
        y=df_cat['cumsum'],
        stackgroup='one',
        line_color=colors[cat],
        # text=[''] * (len(df_cat) - 1) + [df_cat['cumsum'].iloc[-1]],
        # text=df_cat['cumsum'],
        # textposition="top center", texttemplate="%{text:$.4s}",
        # textfont={'color': PRIMARY_COLOR, 'weight': "bold", 'size': 14},
        # hovertemplate='%{x|%b %d, %Y}<br><b>%{y:$.4s}</b><extra></extra>',
        # zorder=2,  # display the line above the brs
        # line={'color': PRIMARY_COLOR, 'width': 3}

    )
    # Add annotation for the last data point
    y_annotation_cumul += df_cat['cumsum'].iloc[-1]
    fig.add_annotation(
        showarrow=False,
        x=df_cat['BM'].iloc[-1],
        y=y_annotation_cumul,
        text=f"${str(df_cat['cumsum'].iloc[-1]):.4s}",
        yshift=15,
        font=dict(size=14, color=colors[cat], weight="bold")
    )
fig.update_xaxes(
    title={'text': 'Board Meeting Number', 'font_size': 16, 'font_weight': "bold"},
    showgrid=False,
    tickprefix='B.',
    dtick=1,
)
fig.update_yaxes(
    title={'text': 'Financing', 'font_size': 16, 'font_weight': "bold"},
    showgrid=False,
)

fig.update_layout(
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    margin={"r": 50, "t": 0, "l": 0, "b": 0, 'autoexpand': True},
    legend=dict(xanchor="left", x=0.05, yanchor="top", y=0.95),
)
FA_timeline = dmc.Stack([
    dcc.Graph(
        id='FA-timeline-graph',
        config={'displayModeBar': False}, responsive=True,
        figure=fig,
        style={"flex": 1}
    )
], p=10, style={"flex": 1})


@callback(
    Output("FA-timeline-graph", "figure"),
    Input("color-scheme-switch", "checked"),
)
def update_figure_theme(checked):
    patched_fig = Patch()
    patched_fig["layout"]["template"] = pio.templates[f"mantine_{'light' if checked else 'dark'}"]
    return patched_fig
