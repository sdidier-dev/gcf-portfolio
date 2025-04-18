import os
from pprint import pprint

from dash import dcc, html, Input, Output, State, callback, no_update, clientside_callback, Patch, ctx
import dash_mantine_components as dmc
import plotly.graph_objects as go
import plotly.io as pio

import pandas as pd

from app_config import df_readiness

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
        texttemplate="%{y}<br>%{x:$.4s} (%{customdata})",
        hovertemplate="<b>%{y}</b><br>%{x:$.4s} (%{customdata})<extra></extra>",

        marker=dict(
            color=status_color[status],
            line={'color': status_color[status], 'width': 3},
            # Trick to add transparency to the color marker only, not the border, as marker_opacity applies to both
            pattern={'fillmode': "replace", 'shape': "/", 'solidity': 1, 'fgcolor': status_color[status],
                     'fgopacity': 0.5}
        ),
    )

fig.update_layout(
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    margin={"r": 0, "t": 0, "l": 0, "b": 50},
    showlegend=False,
    barcornerradius=5,  # radius of the corners of the bars
)
fig.update_xaxes(title={'text': 'Financing', 'standoff': 10, 'font_size': 16, 'font_weight': "bold"},
                 fixedrange=True, showgrid=False, showline=True, linewidth=2, ticks="inside", tickprefix='$')
fig.update_yaxes(showticklabels=False, fixedrange=True, autorange="reversed")


def readiness_status_bar(theme='light'):
    fig.update_layout(template=pio.templates[f"mantine_{theme}"])
    return dcc.Graph(
        id={'type': 'figure', 'subtype': 'bar', 'index': 'readiness-status'},
        config={'displayModeBar': False}, responsive=True,
        figure=fig,
        style={"flex": 1, 'padding': 10}
    )


@callback(
    Output({'type': 'figure', 'subtype': 'bar', 'index': 'readiness-status'}, "figure", allow_duplicate=True),
    Input("readiness-status-carousel", "active"),
    Input({'type': 'grid', 'index': 'readiness'}, "virtualRowData"),
    State({'type': 'figure', 'subtype': 'bar', 'index': 'readiness-status'}, "figure"),
    prevent_initial_call=True
)
def update_status_data(carousel, virtual_data, fig):
    patched_fig = Patch()
    # empty figure if there is no data in the grid
    if not virtual_data:
        for i, trace in enumerate(fig['data']):
            patched_fig["data"][i].update(dict(x=[0], texttemplate='%{y}', textposition='outside'))
        return patched_fig

    # sum financing and number of projects by status
    dff_grid = pd.DataFrame(virtual_data)
    dff = pd.DataFrame(dff_grid.groupby('Status')['Financing'].sum())
    dff['Number'] = dff_grid['Status'].value_counts()

    # carousel 0=Financing, 1=Number
    for i, trace in enumerate(fig['data']):
        status = trace['name']
        if status not in dff.index:
            patched_fig["data"][i].update(dict(x=[0], customdata=[0], texttemplate='%{y}', textposition='outside'))

        else:
            patched_fig["data"][i].update(dict(
                x=[dff['Number'][status] if carousel else dff['Financing'][status]],
                customdata=[dff['Financing'][status] if carousel else dff['Number'][status]],
                textposition='auto'))

        x_template = '%{x}' if carousel else '%{x:$.4s}'
        customdata_template = '%{customdata:$.4s}' if carousel else '%{customdata}'
        patched_fig["data"][i].update(dict(
            texttemplate=f"%{{y}}<br>{x_template} ({customdata_template})",
            hovertemplate=f"<b>%{{y}}</b><br>{x_template} ({customdata_template})<extra></extra>"
        ))

    patched_fig["layout"]['xaxis'].update(dict(
        title={'text': 'Number of Projects' if carousel else 'Financing'},
        tickprefix='' if carousel else '$'
    ))

    return patched_fig
