import os
from pprint import pprint

from dash import dcc, html, Input, Output, State, callback, no_update, clientside_callback, Patch, ctx
import dash_mantine_components as dmc
import plotly.graph_objects as go
import plotly.io as pio

import pandas as pd

from app_config import df_readiness, df_entities, PRIMARY_COLOR


def hovertext_format(row):
    lines = [
        f"<b>{row['Partner Name']}</b><br>",
        f"<u>Country:</u> {row['Partner Country']}<br>" if pd.notna(row['Partner Country']) else '',
        f"<u>Type:</u> {row['Type']}{' (DAE)' if row['DAE'] else ''}<br>" if pd.notna(row['Type']) else '',
        f"<u>Size:</u> {row['Size']}<br>" if pd.notna(row['Size']) else '',
        f"<u>Sector:</u> {row['Sector']}" if pd.notna(row['Sector']) else '',
    ]
    return ''.join(lines)


# Group by 'Delivery Partner' and get both the sum of 'Financing' and the size of each group
dff = df_readiness.groupby('Delivery Partner').agg({
    'Financing': 'sum', 'Delivery Partner': 'size',
    # to keep the info of each partner
    **{col: 'first' for col in ['Partner Name', 'Partner Country', 'DAE', 'Type', 'Size', 'Sector']}
})
dff = dff.rename(columns={'Delivery Partner': 'Number'})
top_partners = dff.sort_values('Financing', ascending=False).head(10)
top_partners['hovertext'] = top_partners.apply(hovertext_format, axis=1)

fig = go.Figure()
fig.add_bar(
    orientation='h',
    x=top_partners['Financing'],
    y=top_partners.index,
    customdata=list(zip(*[top_partners[col] for col in top_partners.columns])),
    texttemplate='<b>%{y}</b> %{customdata[0]:$.4s} (%{customdata[1]} Projects)',
    hoverinfo='text',
    hovertext=top_partners['hovertext'],
    marker=dict(
        color=PRIMARY_COLOR,
        line={'color': PRIMARY_COLOR, 'width': 3},
        # Trick to add transparency to the color marker only, not the border, as marker_opacity applies to both
        pattern={
            'fillmode': "replace", 'shape': "/", 'solidity': 1,
            'fgcolor': PRIMARY_COLOR, 'fgopacity': 0.5
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

readiness_top_partners_bar = dcc.Graph(
    id='readiness-top-partners-bar',
    config={'displayModeBar': False}, responsive=True,
    figure=fig,
    style={"flex": 1, 'padding': 10}
)


@callback(
    Output("readiness-top-partners-bar", "figure", allow_duplicate=True),
    Input("readiness-top-partners-carousel", "active"),
    Input("readiness-top-partners-input", "value"),
    Input("readiness-grid", "virtualRowData"),
    State("readiness-top-partners-bar", "figure"),
    prevent_initial_call=True
)
def update_status_data(carousel, n_top, virtual_data, fig):
    if not virtual_data:
        patched_fig = Patch()
        patched_fig["data"][0]['x'] = None
        patched_fig["data"][0]['y'] = None
        return patched_fig

    # sum financing and number of projects by status
    dff_grid = pd.DataFrame(virtual_data)
    #     dff = pd.DataFrame(dff_grid.groupby('Status')['Financing'].sum())
    dff = dff_grid.groupby('Delivery Partner').agg({
        'Financing': 'sum', 'Delivery Partner': 'size',
        **{col: 'first' for col in ['Partner Name', 'Partner Country', 'DAE', 'Type', 'Size', 'Sector']}
    })
    dff = dff.rename(columns={'Delivery Partner': 'Number'})

    # carousel 0=Financing 1=Number
    data_col = 'Number' if carousel else 'Financing'
    top_partners = dff.sort_values(data_col, ascending=False).head(n_top)
    top_partners['hovertext'] = top_partners.apply(hovertext_format, axis=1)

    patched_fig = Patch()
    patched_fig["data"][0]['x'] = top_partners[data_col]
    patched_fig["data"][0]['y'] = top_partners.index
    patched_fig["data"][0]['customdata'] = list(zip(*[top_partners[col] for col in top_partners.columns]))
    x = '%{x} Projects' if carousel else '%{x:$.4s}'
    customdata = '%{customdata[0]:$.4s}' if carousel else '%{customdata[1]}'
    patched_fig["data"][0]['texttemplate'] = f'<b>%{{y}}</b> {x} ({customdata})'
    patched_fig["data"][0]['hovertext'] = top_partners['hovertext']

    patched_fig["layout"]['xaxis']['title']['text'] = 'Number of Projects' if carousel else 'Financing'
    patched_fig["layout"]['xaxis']['tickprefix'] = '' if carousel else '$'

    return patched_fig


@callback(
    Output("readiness-top-partners-bar", "figure"),
    Input("color-scheme-switch", "checked"),
)
def update_figure_theme(checked):
    patched_fig = Patch()
    patched_fig["layout"]["template"] = pio.templates[f"mantine_{'light' if checked else 'dark'}"]
    return patched_fig
