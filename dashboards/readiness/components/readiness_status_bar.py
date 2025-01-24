import os
from pprint import pprint

from dash import dcc, html, Input, Output, State, callback, no_update, clientside_callback, Patch, ctx
import dash_mantine_components as dmc
import plotly.graph_objects as go
import plotly.io as pio

import pandas as pd

from app_config import df_readiness

# df_readiness.columns

dff = pd.DataFrame(df_readiness.groupby('Status')['Financing'].sum())
dff['Number'] = df_readiness['Status'].value_counts()

status_color = {
    'Cancelled': '#d43a2f', 'In Legal Processing': '#f0ad4e', 'Legal Agreement Effective': '#ffdd33',
    'Disbursed': '#97cd3f', 'Closed': '#15a14a'
}

fig = go.Figure()
for status in status_color.keys():
    fig.add_bar(
        name=status,
        orientation='h',
        x=[dff['Financing'][status]],
        y=[status],
        customdata=[dff['Number'][status]],
        textfont={'textcase': "upper", 'size': 16, 'color': status_color[status], 'weight': "bold"},
        texttemplate="%{y}<br>%{x:$.4s}",
        hovertemplate="<b>%{y}</b><br>%{x:$.4s} (%{customdata} Projects)<extra></extra>",

        marker=dict(
            color=status_color[status],
            line={'color': status_color[status], 'width': 3},
            # Trick to add transparency to the color marker only, not the border,
            # as marker_opacity applies to both
            pattern={
                'fillmode': "replace", 'shape': "/", 'solidity': 1,
                'fgcolor': status_color[status], 'fgopacity': 0.5
            }
        ),
    )

fig.update_layout(
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    margin={"r": 0, "t": 0, "l": 0, "b": 50},
    showlegend=False,
)
fig.update_xaxes(title={'text': 'Financing', 'standoff': 10, 'font_size': 16, 'font_weight': "bold"},
                 showgrid=False, showline=True, linewidth=2, ticks="inside", tickprefix='$')
fig.update_yaxes(showticklabels=False, autorange="reversed")

readiness_status_bar = dcc.Graph(
    id='readiness-status-bar',
    config={'displayModeBar': False}, responsive=True,
    figure=fig,
    style={"flex": 1, 'padding': 10}
)


@callback(
    Output("readiness-status-bar", "figure", allow_duplicate=True),
    Input("readiness-status-bar-carousel", "active"),
    Input("readiness-grid", "virtualRowData"),
    State("readiness-status-bar", "figure"),
    prevent_initial_call=True
)
def update_status_data(carousel, virtual_data, fig):
    if not virtual_data:
        return no_update

    # sum financing and number of projects by status
    dff_grid = pd.DataFrame(virtual_data)
    dff = pd.DataFrame(dff_grid.groupby('Status')['Financing'].sum())
    dff['Number'] = df_readiness['Status'].value_counts()

    patched_fig = Patch()
    for i, trace in enumerate(fig['data']):
        status = trace['name']

        # carousel 0=Financing, 1=Number
        patched_fig["data"][i]['x'] = [dff['Number'][status] if carousel else dff['Financing'][status]]
        patched_fig["data"][i]['customdata'] = [dff['Financing'][status] if carousel else dff['Number'][status]]

        x = '%{x}' if carousel else '%{x:$.4s}'
        customdata = '%{customdata:$.4s} Financing' if carousel else '%{customdata} Projects'
        patched_fig["data"][i]['hovertemplate'] = f"<b>%{{y}}</b><br>{x} ({customdata})<extra></extra>"

        patched_fig["layout"]['xaxis']['title']['text'] = 'Number of Projects' if carousel else 'Financing'
        patched_fig["layout"]['xaxis']['tickprefix'] = '' if carousel else '$'

    return patched_fig


@callback(
    Output("readiness-status-bar", "figure"),
    Input("color-scheme-switch", "checked"),
)
def update_figure_theme(checked):
    patched_fig = Patch()
    patched_fig["layout"]["template"] = pio.templates[f"mantine_{'light' if checked else 'dark'}"]
    return patched_fig
