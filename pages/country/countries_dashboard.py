import os

from dash import Dash, _dash_renderer, Input, Output, State, callback, clientside_callback, Patch, dcc, register_page, \
    MATCH, no_update
import dash_ag_grid as dag

import dash_mantine_components as dmc
from dash_iconify import DashIconify

import pandas as pd

import pages.country.components as components
from app_config import text_carousel

register_page(
    __name__,
    path="/countries",
    # name="W30",  # used as label for the main app navlink
    # title="Rural investments in the US in 2024",  # used by the tooltip for the main app navbar
    # description='The [Rural Development Agency](https://www.rd.usda.gov/about-rd) is part of the US Department of '
    #             'Agriculture and it provides loans, grants, and loan guarantees to bring prosperity and '
    #             'opportunity to rural areas.',
    # image="assets/W30.jpg",  # used by the tooltip for the main app navbar
    # data_source='*Data Source: [USDA-RD website](https://www.rd.usda.gov/rural-data-gateway/rural-investments/data) '
    #             'filtered by fiscal year 2024.*',
    # disabled=False,
)

layout = dmc.Stack(id='countries-container', w='100%', style={"flex": 1}, align='center')


# we use a callback to render the children to be able to provide the theme before they render
# to avoid flickering at init and when switching dashboard
@callback(
    Output('countries-container', "children"),
    Input('countries-container', "id"),
    State("color-scheme-switch", "checked"),
)
def render_children(_, checked):
    theme = 'light' if checked else 'dark'
    return [
        dmc.Group([
            dmc.Card([
                dmc.Center([
                    text_carousel(["Readiness Programme", "Funded Activities"], "countries-map-carousel-1"),
                    text_carousel(["Financing", "Number"], "countries-map-carousel-2"),
                    'by',
                    text_carousel(["Country", "Region"], "countries-map-carousel-3"),
                ], className='card-header', fz=20, h=40, style={'gap': 5, 'border-radius': '8px 8px 0px 0px'}),
                dmc.Divider(),
                components.countries_map(theme)
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
                ], className='card-header', fz=20, h=40,
                    style={'gap': 5, 'border-radius': '8px 8px 0px 0px'}),
                dmc.Divider(),

                components.countries_parcats(theme)

            ],
                withBorder=True, shadow="sm", radius='md',
                mt=10,  # NOTE: add a margin to allow the overflow of the text Carousel control
                miw=600, mih=300, style={"flex": 1, 'overflow': 'visible'}, p=0
            )
        ], style={"flex": 1, 'flex-wrap': 'wrap', 'overflow': 'auto'}, align='stretch', w='100%'),
        dmc.Group([
            dmc.Button("Reset Filters", id={"type": "reset-filter-btn", "index": 'countries'},
                       variant="outline", color='var(--primary)',
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

        components.countries_grid(theme)

    ]
