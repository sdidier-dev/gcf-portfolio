import os
from pprint import pprint

from dash import dcc, html, Input, Output, State, callback, no_update, clientside_callback, Patch, ctx
import dash_mantine_components as dmc
import plotly.graph_objects as go
import plotly.io as pio

import pandas as pd

from app_config import df_countries


def format_df_for_parcats(df):
    for col in ['priority state', 'SIDS', 'LDC', 'AS']:
        df[col] = df[col].apply(lambda x: 'Yes' if x is True else 'No')
    df['Region'] = df['Region'].apply(
        lambda x: 'Latin America<br>and the Caribbean' if 'Latin' in x
        else 'Western Europe<br>and Others' if 'Western' in x
        else x
    )
    return df


dff = format_df_for_parcats(df_countries.copy())

dimensions = [
    go.parcats.Dimension(label=col.upper(), values=dff[col], categoryorder='category descending')
    for col in ['priority state', 'SIDS', 'LDC', 'AS']
]

dimensions.append(
    go.parcats.Dimension(label='REGION', values=dff['Region'], categoryorder='category ascending')
)

fig = go.Figure()
fig.add_parcats(
    dimensions=dimensions,
    counts=dff['FA Financing $'],
    line={'shape': 'hspline', 'colorscale': [[0, '#a0a115'], [1, '#15a14a']], 'color': '#15a14a'},
    hoveron='color',
    labelfont_size=16,
    tickfont_size=14,
    hovertemplate="%{bandcolorcount:$.4s} Financing<br>"
                  "%{probability:.0%} of overall",
    line_hovertemplate="%{count:$.4s}<br>"
                       "%{probability:.0%} of overall",
)

fig.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    margin={"t": 30, "r": 70, "b": 30, "l": 20},
)

countries_parcats = dmc.Stack([
    dmc.Tooltip(
        dmc.Checkbox(id="countries-parcats-chk", label="Highlight Priority States Lines", fz=16),
        multiline=True, withArrow=True, arrowSize=6, w=300, position="bottom",
        label="States categorized in at least one priority group SIDS/LDC/AS",
        bg='var(--mantine-color-body)', c='var(--mantine-color-text)', bd='1px solid var(--primary)',
        styles={
            'arrow': {'border-top': '1px solid var(--primary)', 'border-left': '1px solid var(--primary)'},
        },
    ),
    dcc.Graph(
        id='countries-parcats',
        config={'displayModeBar': False},
        responsive=True,
        figure=fig,
        style={"flex": 1}
    )
], p=10, style={"flex": 1})


@callback(
    Output("countries-parcats", "figure", allow_duplicate=True),
    Input("countries-parcats-carousel-1", "active"),
    Input("countries-parcats-carousel-2", "active"),
    Input("countries-grid", "virtualRowData"),
    prevent_initial_call=True
)
def update_parcats_data(carousel_1, carousel_2, virtual_data):
    patched_fig = Patch()
    if not virtual_data:
        for i, dim in enumerate(['priority state', 'SIDS', 'LDC', 'AS', 'Region']):
            patched_fig["data"][0]['dimensions'][i]['values'] = None
        return patched_fig

    dff = format_df_for_parcats(pd.DataFrame(virtual_data))

    col = 'FA' if carousel_1 else 'RP'  # 0=Readiness, 1=Funded Activities
    col = f"# {col}" if carousel_2 else f"{col} Financing $"  # 0=Financing, 1=Number

    patched_fig["data"][0]['counts'] = dff[col]

    for i, dim in enumerate(['priority state', 'SIDS', 'LDC', 'AS', 'Region']):
        patched_fig["data"][0]['dimensions'][i]['values'] = dff[dim]

    patched_fig["data"][0]['hovertemplate'] = (
        f"%{{bandcolorcount{'' if carousel_2 else ':$.4s'}}} {'Projects' if carousel_2 else 'Financing'}"
        f"<br>%{{probability:.0%}} of overall"
    )

    patched_fig["data"][0]['line']['hovertemplate'] = (
        f"%{{count{'' if carousel_2 else ':$.4s'}}} {'Projects' if carousel_2 else 'Financing'}"
        f"<br>%{{probability:.0%}} of overall"
    )

    return patched_fig


@callback(
    Output("countries-parcats", "figure", allow_duplicate=True),
    Input("countries-parcats-chk", "checked"),
    Input("countries-grid", "virtualRowData"),
    prevent_initial_call=True
)
def highlight_priority_countries(checked, virtual_data):
    if not virtual_data:
        return no_update

    dff = format_df_for_parcats(pd.DataFrame(virtual_data))
    color = dff['priority state'].apply(lambda x: 0 if x == 'Yes' else 1) if checked else '#15a14a'

    patched_fig = Patch()
    patched_fig["data"][0]['line']['color'] = color
    return patched_fig

@callback(
    Output("countries-parcats", "figure"),
    Input("color-scheme-switch", "checked"),
)
def update_figure_theme(checked):
    patched_fig = Patch()
    patched_fig["layout"]["template"] = pio.templates[f"mantine_{'light' if checked else 'dark'}"]
    return patched_fig
