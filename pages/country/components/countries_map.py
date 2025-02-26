import json
import os
from pprint import pprint

from dash import dcc, html, Input, Output, State, callback, no_update, clientside_callback, Patch, ctx
import dash_mantine_components as dmc
import plotly.graph_objects as go
import plotly.io as pio

import pandas as pd

from app_config import df_countries

fig = go.Figure()

fig.add_choropleth(
    locations=df_countries['ISO3'],
    z=df_countries['FA Financing $'],
    colorscale='greens',
    colorbar_tickprefix='$',
    customdata=list(zip(df_countries['# RP'], df_countries['Country Name'])),
    hovertemplate='%{z:$.4s} (%{customdata[0]})<extra>%{customdata[1]}</extra>'
)

# Add map traces to highlight the priority states
priority_states_groups = {'SIDS': '#ff6b6b', 'LDC': '#ff922b', 'AS': '#fcc419'}
for group in priority_states_groups:
    df_group = df_countries[df_countries[group]]

    fig.add_choropleth(
        visible=False,  # will be visible using the Chips
        name=group.lower(),
        locations=df_group['ISO3'],
        # fake data using transparent markers, to use only the border
        z=[1] * len(df_group),
        colorscale=[[0, 'rgba(0,0,0,0)'], [1, 'rgba(0,0,0,0)']],
        hoverinfo='skip',
        showscale=False,
        marker_line_color=priority_states_groups[group],
        marker_line_width=2,
    )

fig.update_layout(
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    geo=dict(
        center={'lat': -1.2, 'lon': 28.5}, projection={'scale': 1.15},
        bgcolor='rgba(0,0,0,0)', countrycolor='rgba(0,0,0,0)',
        showframe=False, showlakes=False, showcountries=True,
    )
)


def countries_map(theme='light'):
    fig.update_layout(template=pio.templates[f"mantine_{theme}"],
                      geo_landcolor='#f1f3f5' if theme == 'light' else '#1f1f1f')
    return dmc.Stack([
        dmc.Group(
            [
                'Show Priority States:',
                dmc.ChipGroup(
                    [dmc.Chip(group, value=group.lower(), color=priority_states_groups[group])
                     for group in priority_states_groups],
                    id="countries-map-chipgroup",
                    multiple=True,
                    # persistence=True, persisted_props=["value"]
                ),
                'Scope',
                dmc.Select(
                    id="countries-map-dropdown",
                    data=["World", "Africa", "Asia", "Europe", "North America", "South America"],
                    value="World",
                    checkIconPosition='right', w=150,
                    comboboxProps={'transitionProps': {'duration': 300, 'transition': 'scale-y'}},
                ),
            ]
        ),
        dcc.Graph(
            id={'type': 'figure', 'subtype': 'map', 'index': 'countries'},
            config={'displayModeBar': False},
            responsive=True,
            figure=fig,
            style={'height': '100%'},
        )
    ], p=10, style={"flex": 1})


@callback(
    Output({'type': 'figure', 'subtype': 'map', 'index': 'countries'}, "figure", allow_duplicate=True),
    Input("countries-map-carousel-1", "active"),
    Input("countries-map-carousel-2", "active"),
    Input("countries-map-carousel-3", "active"),
    Input({'type': 'grid', 'index': 'countries'}, "virtualRowData"),
    prevent_initial_call=True
)
def update_map_data(carousel_1, carousel_2, carousel_3, virtual_data):
    patched_fig = Patch()
    if not virtual_data:
        patched_fig["data"][0]['z'] = None
        return patched_fig

    dff = pd.DataFrame(virtual_data)

    activity = 'FA' if carousel_1 else 'RP'  # 0=Readiness, 1=Funded Activities

    # financing|# and None|region_sum
    z_col = f"# {activity}" if carousel_2 else f"{activity} Financing $"  # 0=Financing, 1=Number
    z_col = f"{z_col} region_sum" if carousel_3 else z_col  # 0=by country, 1=by region
    # format label depending on financing|#
    z_format = '' if carousel_2 else ':$.4s'

    # complementary data of z_col
    customdata_0_col = f"{activity} Financing $" if carousel_2 else f"# {activity}"
    customdata_0_col = f"{customdata_0_col} region_sum" if carousel_3 else customdata_0_col
    # customdata for <extra> part 'Country Name'|"Region"
    customdata_1_col = "Region" if carousel_3 else 'Country Name'
    # format label depending on financing|#
    customdata_0_format = ':$.4s' if carousel_2 else ''

    patched_fig["data"][0].update(dict(
        locations=dff['ISO3'],
        z=dff[z_col],
        customdata=list(zip(dff[customdata_0_col], dff[customdata_1_col])),
        hovertemplate=f'%{{z{z_format}}} (%{{customdata[0]{customdata_0_format}}})<extra>%{{customdata[1]}}</extra>',
        colorbar={'tickformat': '' if carousel_2 else '$.4s'},
    ))

    return patched_fig


@callback(
    Output({'type': 'figure', 'subtype': 'map', 'index': 'countries'}, "figure", allow_duplicate=True),
    Input("countries-map-chipgroup", "value"),
    State({'type': 'figure', 'subtype': 'map', 'index': 'countries'}, "figure"),
    prevent_initial_call=True
)
def show_priority_states(values, fig):
    patched_fig = Patch()
    for i, t in enumerate(fig['data']):
        if 'name' in t:  # skip the main map
            patched_fig["data"][i]['visible'] = t['name'] in values
    return patched_fig


@callback(
    Output({'type': 'figure', 'subtype': 'map', 'index': 'countries'}, "figure", allow_duplicate=True),
    Input("countries-map-dropdown", "value"),
    prevent_initial_call=True
)
def update_map_scope(scope):
    scope_frame = {
        'world': {'center': {'lat': -1.2, 'lon': 28.5}, 'projection': {'scale': 1.15}},
        'africa': {'center': {'lat': 0, 'lon': 15}, 'projection': {'scale': 1}},
        'asia': {'center': {'lat': 24, 'lon': 82}, 'projection': {'scale': 1.1}},
        'europe': {'center': {'lat': 52, 'lon': 15}, 'projection': {'scale': 1.7}},
        'north america': {'center': {'lat': 29, 'lon': -92}, 'projection': {'scale': 2}},
        'south america': {'center': {'lat': -27, 'lon': -66}, 'projection': {'scale': 1}},
    }
    patched_fig = Patch()
    patched_fig["layout"]['geo']['scope'] = scope.lower()
    patched_fig["layout"]['geo']['center'] = scope_frame[scope.lower()]['center']
    patched_fig["layout"]['geo']['projection'] = scope_frame[scope.lower()]['projection']
    return patched_fig

