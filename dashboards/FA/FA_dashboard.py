import os

from dash import Dash, _dash_renderer, Input, Output, State, callback, clientside_callback, Patch, ctx, ALL
import dash_ag_grid as dag

import dash_mantine_components as dmc
from dash_iconify import DashIconify

import pandas as pd
from dash import Dash, html, Input, Output, register_page, clientside_callback, dcc, callback, State
import dashboards.FA.components as components
from app_config import text_carousel

FA_dashboard = dmc.Stack([
    dmc.Group([

        dmc.Card([
            dmc.Center([
                "Approved Projects",
                text_carousel(["Financing", "Number"], "fa-timeline-carousel1"),
                "by",
                text_carousel(components.cat_cols.keys(), "fa-timeline-carousel2"),
            ], id={"type": "card-header", "index": 'fa-timeline'}, fz=20, h=40,
                style={'gap': 5, 'border-radius': '8px 8px 0px 0px'}),
            dmc.Divider(),
            components.FA_timeline
        ], withBorder=True, shadow="sm", radius='md',
            p=0, mt=10,  # NOTE: add a margin to allow the overflow of the text Carousel control
            miw=500, mih=400, style={"flex": 2, 'overflow': 'visible'}
        ),
        dmc.Card([
            dmc.Center([
                "Projects",
                text_carousel(["Financing", "Number"], "fa-bar-carousel"),
                "Distribution by Categories",
            ], id={"type": "card-header", "index": 'fa-bar'}, fz=20, h=40,
                style={'gap': 5, 'border-radius': '8px 8px 0px 0px'}),
            dmc.Divider(),
            components.FA_bar
        ], withBorder=True, shadow="sm", radius='md',
            p=0, mt=10,  # NOTE: add a margin to allow the overflow of the text Carousel control
            miw=600, mih=400, style={"flex": 2, 'overflow': 'visible'}
        ),
        dmc.Card([
            dmc.Center([
                "Projects Financing Distribution",
            ], id={"type": "card-header", "index": 'fa-histogram'}, fz=20, h=40,
                style={'gap': 5, 'border-radius': '8px 8px 0px 0px'}),
            dmc.Divider(),
            components.FA_histogram
        ], withBorder=True, shadow="sm", radius='md',
            p=0, mt=10,  # NOTE: add a margin to allow the overflow of the text Carousel control
            miw=400, mih=400, style={"flex": 1, 'overflow': 'visible'}
        ),

            ], style={"flex": 1, 'flex-wrap': 'wrap', 'overflow': 'auto'}, align='stretch', w='100%'
    ),
    dmc.Group([
        dmc.Text('Pro tip:', size="xs", c="dimmed", td="underline"),
        dmc.Text('The Graphs above are linked to the data of the Grid, filtering the data of the Grid will '
                 'update the Graphs accordingly.', size="xs", c="dimmed")
    ], style={"align-self": 'flex-start'}),
    components.FA_grid
], w='100%', style={"flex": 1}, align='center')


@callback(
    Output({"type": "card-header", "index": ALL}, "style"),
    Input("color-scheme-switch", "checked"),
)
def fa_card_switch_theme(checked):
    card_patch = Patch()
    card_patch['background-color'] = f"var(--mantine-color-{'gray-1' if checked else 'dark-8'})"
    return [card_patch] * len(ctx.outputs_list)
