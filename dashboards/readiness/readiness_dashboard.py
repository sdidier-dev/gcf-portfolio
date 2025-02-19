import os

from dash import Dash, _dash_renderer, Input, Output, State, callback, clientside_callback, Patch, dcc
import dash_ag_grid as dag

import dash_mantine_components as dmc
from dash_iconify import DashIconify

import pandas as pd

import dashboards.readiness.components as components
from app_config import text_carousel

# Seeds of Climate Action: Readiness Programme Flow of Funds

readiness_dashboard = dmc.Stack([
    # dmc.Group([
    #     dmc.Card([
    #         'cool'
    #     ], style={
    #         'box-shadow': '0 0 10px var(--primary)',
    #         'border-color': 'var(--primary)'
    #     }
    #     )
    # ], style={
    #     'border': '1px solid red',
    # }
    # ),

    dmc.Group([

        dmc.Card([
            dmc.Center([
                "Readiness Programme Flow of Funds"
            ], id='readiness-timeline-card-header', fz=20, h=40, style={'gap': 5, 'border-radius': '8px 8px 0px 0px'}),
            dmc.Divider(),

            components.readiness_timeline

        ],
            withBorder=True, shadow="sm", radius='md',
            mt=10,  # NOTE: add a margin to allow the overflow of the text Carousel control
            miw=600, mih=400, style={"flex": 1, 'overflow': 'visible'}, p=0
        ),

        dmc.Group([
            dmc.Card([
                dmc.Center([
                    "Readiness Programmes",
                    text_carousel(["Financing", "Number"], "readiness-status-carousel"),
                    "by Status"
                ], id='readiness-status-card-header', fz=20, h=40,
                    style={'gap': 5, 'border-radius': '8px 8px 0px 0px'}),
                dmc.Divider(),

                components.readiness_status_bar

            ],
                withBorder=True, shadow="sm", radius='md',
                mt=10,  # NOTE: add a margin to allow the overflow of the text Carousel control
                miw=400, mih=300, style={"flex": 1, 'overflow': 'visible'}, p=0
            ),
            dmc.Card([
                dmc.Center([
                    'Top ',
                    dmc.NumberInput(
                        id='readiness-top-partners-input', variant='unstyled', value=10, min=1, w=50,
                        size='xs', ml=5,
                        styles={
                            'wrapper': {'display': 'flex'},
                            "input": {'color': 'var(--primary)', 'font-size': 20, 'font-weight': 'bold',
                                      'text-align': 'center', 'text-decoration': 'underline', 'width': 25,
                                      'padding': 0},
                            'section': {'position': 'relative', 'width': 15},
                        },
                    ),
                    'Partners by',
                    text_carousel(["Financing", "Project Number"], "readiness-top-partners-carousel"),
                ], id='readiness-top-partners-card-header', fz=20, h=40,
                    style={'border-radius': '8px 8px 0px 0px'}),
                dmc.Divider(),

                components.readiness_top_partners_bar

            ],
                withBorder=True, shadow="sm", radius='md',
                mt=10,  # NOTE: add a margin to allow the overflow of the text Carousel control
                miw=400, mih=330, style={"flex": 1, 'overflow': 'visible'}, p=0
            )
        ], style={"flex": 1, 'height': '100%', 'flex-wrap': 'wrap', 'overflow': 'auto', 'row-gap': 0},
            # remove the row gap, when they are w raped the cards already have the top margin
            align='stretch', miw=400
        ),

    ], style={"flex": 1, 'flex-wrap': 'wrap', 'overflow': 'auto'}, align='stretch', w='100%'
    ),
    dmc.Group([
        dmc.Button("Reset Grid Filters", id='readiness-grid-reset-btn', variant="outline", color='var(--primary)',
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

    components.readiness_grid

], w='100%', style={"flex": 1}, align='center')


@callback(
    Output("readiness-timeline-card-header", "style"),
    Output("readiness-status-card-header", "style"),
    Output("readiness-top-partners-card-header", "style"),
    Input("color-scheme-switch", "checked"),
)
def readiness_card_switch_theme(checked):
    card_patch = Patch()
    card_patch['background-color'] = f"var(--mantine-color-{'gray-1' if checked else 'dark-8'})"
    return card_patch, card_patch, card_patch
