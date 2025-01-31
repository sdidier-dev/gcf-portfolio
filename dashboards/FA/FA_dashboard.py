import os

from dash import Dash, _dash_renderer, Input, Output, State, callback, clientside_callback, Patch
import dash_ag_grid as dag

import dash_mantine_components as dmc
from dash_iconify import DashIconify

import pandas as pd
from dash import Dash, html, Input, Output, register_page, clientside_callback, dcc, callback, State
import dashboards.FA.components as components

FA_dashboard = dmc.Stack([
    dmc.Group([
        dmc.Card([
            dmc.Center([
                "Board Approved Funded Activities by Theme"
            ], id='FA-timeline-card-header', fz=20, h=40, style={'gap': 5, 'border-radius': '8px 8px 0px 0px'}),
            dmc.Divider(),
            components.FA_timeline
        ],
            withBorder=True, shadow="sm", radius='md',
            mt=10,  # NOTE: add a margin to allow the overflow of the text Carousel control
            miw=600, mih=400, style={"flex": 1, 'overflow': 'visible'}, p=0
        ),

    ], style={"flex": 1, 'flex-wrap': 'wrap', 'overflow': 'auto'}, align='stretch', w='100%'
    ),
    components.FA_grid
], w='100%', style={"flex": 1}, align='center')


@callback(
    Output("FA-timeline-card-header", "style"),
    Input("color-scheme-switch", "checked"),
)
def readiness_card_switch_theme(checked):
    card_patch = Patch()
    card_patch['background-color'] = f"var(--mantine-color-{'gray-1' if checked else 'dark-8'})"
    return card_patch
