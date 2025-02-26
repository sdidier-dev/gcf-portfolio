import json
import os
from pprint import pprint

from dash import dcc, html, Input, Output, State, callback, no_update, clientside_callback, Patch, ctx
import dash_mantine_components as dmc
import plotly.graph_objects as go
import plotly.io as pio

import pandas as pd

from app_config import df_entities, PRIMARY_COLOR, format_money_number_si

# dataset for the entities map
dff = df_entities.groupby('Country').agg(
    {'Alpha-3 code': 'first', 'Entity': 'count', '# Approved': 'sum', 'FA Financing': 'sum'}).reset_index()


# add col for hover data aggregating entities names and acronym and restrict the nb of char by line
def join_names(group, max_chars_per_line=70):
    names = []
    for entity, name in zip(group['Entity'], group['Name']):
        item = f"<b>{entity}</b> ({name})"
        if len(item) > max_chars_per_line:
            item = item[:max_chars_per_line - 3] + "..."  # Truncate and add ellipsis
        names.append(item)
    return '<br>'.join(names)


names_column = df_entities.groupby('Country').apply(
    join_names, include_groups=False, max_chars_per_line=70).reset_index()
names_column.rename(columns={0: 'Names'}, inplace=True)

dff = pd.merge(dff, names_column, on='Country')

fig = go.Figure()

fig.add_choropleth(
    locations=dff['Alpha-3 code'],
    z=dff['Entity'], zmin=0, zmax=6,
    colorscale='greens',
    colorbar_tickprefix='$',
    customdata=list(zip(dff['Entity'], dff['# Approved'],
                        # use custom function to have $1B instead of $1G, as it is not possible with D3-formatting
                        [format_money_number_si(val) for val in dff['FA Financing']],
                        dff['Names'], dff['Country'])),
    hovertemplate='Entity Number: <b>%{customdata[0]}</b><br>'
                  'FA Number: <b>%{customdata[1]}</b><br>'
                  'FA Financing: <b>%{customdata[2]}</b><extra><b>%{customdata[4]}</b></extra>'
)

fig.update_layout(
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    geo=dict(
        center={'lat': -1.2, 'lon': 28.5}, projection={'scale': 1.15},
        bgcolor='rgba(0,0,0,0)', countrycolor='rgba(0,0,0,0)',
        showframe=False, showlakes=False, showcountries=True,
    ),
)

# data distribution fig used as elp for the colorbar range control
fig_distrib = go.Figure()
fig_distrib.add_histogram(
    x=dff['Entity'],
    marker_color=PRIMARY_COLOR,
    xbins_start=0, nbinsx=20,
    hovertemplate="<b>%{y}</b> Countries having<br>"
                  "<b>%{x}</b> Entities<extra></extra>",
)
fig_distrib.update_layout(
    title=dict(text='Entities Number distribution', font_size=12, x=1, xanchor='right', y=0.95, yanchor='top'),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis_fixedrange=True,
    yaxis_showgrid=False,
    yaxis_range=[0, 70],
    margin={"r": 0, "t": 0, "l": 0, "b": 15},
)


def entities_map(theme='light'):
    fig.update_layout(template=pio.templates[f"mantine_{theme}"],
                      geo_landcolor='#f1f3f5' if theme == 'light' else '#1f1f1f')
    fig_distrib.update_layout(template=pio.templates[f"mantine_{theme}"])
    return dmc.Stack([
        dmc.Group([
            dmc.Checkbox(id="entities-map-hover-chk", label="Show Entities Names on Hover", w=150,
                         styles={'body': {'align-items': 'center'}}),
            dmc.Stack([
                dcc.Graph(
                    id={'type': 'figure', 'index': 'entities-map-distrib'},
                    config={'displayModeBar': False},
                    responsive=True,
                    figure=fig_distrib,
                    style={'flex': 1}
                ),
                dmc.Slider(
                    id="entities-map-distrib-slider",
                    min=0, max=dff['Entity'].max(), value=6,
                    color=PRIMARY_COLOR, size=2, pl=15, my=5,
                    showLabelOnHover=False,
                ),
                dmc.Text("Use the Slider to adapt the colorbar range", size="xs", c="dimmed", pl=10),

            ], style={'gap': 0, 'height': 100})
        ], fz=14, justify='space-around',
        ),
        dcc.Graph(
            id={'type': 'figure', 'subtype': 'map', 'index': 'entities'},
            config={'displayModeBar': False}, responsive=True,
            figure=fig,
            style={'height': '100%'},
        )
    ], p=10, style={"flex": 1})


@callback(
    Output({'type': 'figure', 'subtype': 'map', 'index': 'entities'}, "figure", allow_duplicate=True),
    Output({'type': 'figure', 'index': 'entities-map-distrib'}, "figure", allow_duplicate=True),
    Output("entities-map-distrib-slider", "value", allow_duplicate=True),
    Output("entities-map-distrib-slider", "max", allow_duplicate=True),
    Input("entities-map-carousel", "active"),
    Input({'type': 'grid', 'index': 'entities'}, "virtualRowData"),
    prevent_initial_call=True
)
def update_map_distrib_data(carousel, virtual_data):
    patched_fig = Patch()
    patched_fig_distrib = Patch()

    if not virtual_data:
        patched_fig["data"][0]['z'] = None
        patched_fig_distrib["data"][0]['x'] = None
        return patched_fig, patched_fig_distrib, None, None

    dff = pd.DataFrame(virtual_data)

    names_column = dff.groupby('Country').apply(
        lambda x: join_names(x, max_chars_per_line=70)).reset_index()
    names_column.rename(columns={0: 'Names'}, inplace=True)

    dff = dff.groupby('Country').agg(
        {'Alpha-3 code': 'first', 'Entity': 'count', '# Approved': 'sum', 'FA Financing': 'sum'}).reset_index()

    dff = pd.merge(dff, names_column, on='Country')

    # carousel 0=entities number 1=FA financing 2=FA number
    if carousel == 0:
        data = dff['Entity']
        tickprefix = None
        distrib_title = 'Entities Number Distribution'
        hovertemplate = ("<b>%{y}</b> Countries having<br>"
                         "<b>%{x}</b> Entities<extra></extra>")
        slider_value = 6
        slider_max = dff['Entity'].max()
    elif carousel == 1:
        data = dff['FA Financing']
        tickprefix = '$'
        distrib_title = 'FA Financing Distribution'
        hovertemplate = ("<b>%{y}</b>  Entities' Home Countries<br>"
                         "With a total FA Financing in the Range<b>[%{x}]</b><extra></extra>")
        slider_value = 500 * 10 ** 6
        slider_max = dff['FA Financing'].max()
    else:
        data = dff['# Approved']
        tickprefix = None
        distrib_title = 'FA Number Distribution'
        hovertemplate = ("<b>%{y}</b> Entities' Home Countries<br>"
                         "With a total FA Number in the Range<b>[%{x}]</b><extra></extra>")
        slider_value = 10
        slider_max = dff['# Approved'].max()

    # update map data
    patched_fig["data"][0].update(dict(
        z=data, locations=dff['Alpha-3 code'],
        colorbar=dict(tickprefix=tickprefix),
        customdata=list(zip(
            dff['Entity'], dff['# Approved'],
            # use custom function to have $1B instead of $1G, as it is not possible with D3-formatting
            [format_money_number_si(val) for val in dff['FA Financing']],
            dff['Names'], dff['Country'])),
    ))

    # update distrib control data and layout
    patched_fig_distrib["data"][0].update(
        dict(x=data, hovertemplate=hovertemplate)
    )

    patched_fig_distrib["layout"]['xaxis']['tickprefix'] = tickprefix
    patched_fig_distrib["layout"]['title']['text'] = distrib_title

    # fix hover text overflow
    return patched_fig, patched_fig_distrib, slider_value, slider_max


@callback(
    Output({'type': 'figure', 'subtype': 'map', 'index': 'entities'}, "figure", allow_duplicate=True),
    Input("entities-map-hover-chk", "checked"),
    prevent_initial_call=True
)
def entities_names_on_hover(show_names):
    patched_fig = Patch()
    hovertemplate = ('Entity Number: <b>%{customdata[0]}</b><br>'
                     'FA Number: <b>%{customdata[1]}</b><br>'
                     'FA Financing: <b>%{customdata[2]}</b><br><br>')
    if show_names:
        hovertemplate += '%{customdata[3]}'
    hovertemplate += '<extra><b>%{customdata[4]}</b></extra>'

    patched_fig["data"][0]['hovertemplate'] = hovertemplate
    return patched_fig


@callback(
    Output({'type': 'figure', 'subtype': 'map', 'index': 'entities'}, "figure", allow_duplicate=True),
    Input("entities-map-distrib-slider", "value"),
    prevent_initial_call=True
)
def update_colorbar(value):
    patched_fig = Patch()
    patched_fig["data"][0]['zmax'] = value
    return patched_fig
