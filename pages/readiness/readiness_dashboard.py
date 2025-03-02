import os

from dash import Dash, _dash_renderer, Input, Output, State, callback, clientside_callback, Patch, dcc, register_page
import dash_ag_grid as dag

import dash_mantine_components as dmc
from dash_iconify import DashIconify

import pandas as pd

import pages.readiness.components as components
from app_config import text_carousel

# Seeds of Climate Action: Readiness Programme Flow of Funds
register_page(__name__, path="/readiness")

layout = dmc.Stack(id='readiness-container', w='100%', style={"flex": 1}, align='center')


# we use a callback to render the children to be able to provide the theme before they render
# to avoid flickering at init and when switching dashboard
@callback(
    Output('readiness-container', "children"),
    Input('readiness-container', "id"),
    State("color-scheme-switch", "checked"),
)
def render_children(_, checked):
    theme = 'light' if checked else 'dark'
    return [
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
                ], className='card-header', fz=20, h=40, style={'gap': 5, 'borderRadius': '8px 8px 0px 0px'}),
                dmc.Divider(),

                components.readiness_timeline(theme)

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
                    ], className='card-header', fz=20, h=40,
                        style={'gap': 5, 'borderRadius': '8px 8px 0px 0px'}),
                    dmc.Divider(),

                    components.readiness_status_bar(theme)

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
                                "input": {'color': 'var(--primary)', 'fontSize': 20, 'fontWeight': 'bold',
                                          'textAlign': 'center', 'textDecoration': 'underline', 'width': 25,
                                          'padding': 0},
                                'section': {'position': 'relative', 'width': 15},
                            },
                        ),
                        'Partners by',
                        text_carousel(["Financing", "Project Number"], "readiness-top-partners-carousel"),
                    ], className='card-header', fz=20, h=40,
                        style={'borderRadius': '8px 8px 0px 0px'}),
                    dmc.Divider(),

                    components.readiness_top_partners_bar(theme)

                ],
                    withBorder=True, shadow="sm", radius='md',
                    mt=10,  # NOTE: add a margin to allow the overflow of the text Carousel control
                    miw=400, mih=330, style={"flex": 1, 'overflow': 'visible'}, p=0
                )
            ], style={"flex": 1, 'height': '100%', 'flexWrap': 'wrap', 'overflow': 'auto', 'row-gap': 0},
                # remove the row gap, when they are w raped the cards already have the top margin
                align='stretch', miw=400
            ),

        ], style={"flex": 1, 'flexWrap': 'wrap', 'overflow': 'auto'}, align='stretch', w='100%'),

        dmc.Group([
            dmc.Button("Reset Filters", id={"type": "reset-filter-btn", "index": 'readiness'},
                       variant="outline", color='var(--primary)',
                       size='compact-xs', radius="lg", px=10, style={"alignSelf": 'center '}),
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
        ], style={"alignSelf": 'center'}),

        components.readiness_grid(theme)

    ]
