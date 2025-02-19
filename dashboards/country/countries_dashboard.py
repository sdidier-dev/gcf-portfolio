import os

from dash import Dash, _dash_renderer, Input, Output, State, callback, clientside_callback, Patch, dcc
import dash_ag_grid as dag

import dash_mantine_components as dmc
from dash_iconify import DashIconify

import pandas as pd

import dashboards.country.components as components
from app_config import text_carousel

countries_dashboard = dmc.Stack([
    dmc.Group([
        dmc.Card([
            dmc.Center([
                text_carousel(["Readiness Programme", "Funded Activities"], "countries-map-carousel-1"),
                text_carousel(["Financing", "Number"], "countries-map-carousel-2"),
                'by',
                text_carousel(["Country", "Region"], "countries-map-carousel-3"),
            ], id='countries-card-header-map', fz=20, h=40, style={'gap': 5, 'border-radius': '8px 8px 0px 0px'}),
            dmc.Divider(),
            components.countries_map
        ],
            withBorder=True, shadow="sm", radius='md',
            mt=10,  # NOTE: add a margin to allow the overflow of the text Carousel control
            miw=600, mih=300, style={"flex": 1, 'overflow': 'visible'}, p=0
        ),
        dmc.Card([
            dmc.Center([
                text_carousel(["Readiness Programme", "Funded Activities"], "countries-parcats-carousel-1"),
                text_carousel(["Financing", "Number"], "countries-parcats-carousel-2"),
                'Distribution',
            ], id='countries-card-header-parcats', fz=20, h=40, style={'gap': 5, 'border-radius': '8px 8px 0px 0px'}),
            dmc.Divider(),

            components.countries_parcats

        ],
            withBorder=True, shadow="sm", radius='md',
            mt=10,  # NOTE: add a margin to allow the overflow of the text Carousel control
            miw=600, mih=300, style={"flex": 1, 'overflow': 'visible'}, p=0
        )
    ], style={"flex": 1, 'flex-wrap': 'wrap', 'overflow': 'auto'}, align='stretch', w='100%'),
    dmc.Group([
        dmc.Button("Reset Grid Filters", id='countries-grid-reset-btn', variant="outline", color='var(--primary)',
                   size='compact-xs', radius="lg", px=10, style={"align-self": 'center '}),
        dmc.Tooltip(
            dmc.Center(DashIconify(icon='clarity:info-line', color='var(--primary)', width=25)),
            label=[
                dcc.Markdown(
                    '<u>Pro tip:</u><br>'
                    'The Grid and the Graphs are linked.<br>'
                    'Try to filter the Grid or click on the Graphs.',
                    dangerously_allow_html=True, style={'margin': 0}, className='no-margin-markdown'),
            ],
            multiline=True, withArrow=True, arrowSize=6, position="right",
            bg='var(--mantine-color-body)', c='var(--mantine-color-text)',
            transitionProps={"transition": "scale-x", "duration": 300},
        ),
    ], style={"align-self": 'center'}),

    components.countries_grid

], w='100%', style={"flex": 1}, align='center')


@callback(
    Output("countries-card-header-map", "style"),
    Output("countries-card-header-parcats", "style"),
    Input("color-scheme-switch", "checked"),
)
def countries_card_switch_theme(checked):
    card_patch = Patch()
    card_patch['background-color'] = f"var(--mantine-color-{'gray-1' if checked else 'dark-8'})"
    return card_patch, card_patch
