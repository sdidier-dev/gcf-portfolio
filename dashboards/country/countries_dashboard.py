import os

from dash import Dash, _dash_renderer, Input, Output, State, callback, clientside_callback, Patch
import dash_ag_grid as dag

import dash_mantine_components as dmc
from dash_iconify import DashIconify

import pandas as pd

import dashboards.country.components as components


def text_carousel(text_list: list[str], carousel_id: str):
    return dmc.Carousel(
        [dmc.CarouselSlide(dmc.Center(text, h='100%', fw='bold', td='underline', c='var(--primary)')) for text in
         text_list],
        id=carousel_id,
        orientation="vertical",
        height=40,
        # remove the padding, so the controls are at the max top/bottom of the Carousel
        controlsOffset=-50,
        controlSize=15,
        # custom class to Hide inactive controls and Show controls on hover
        classNames={"control": "carousel-control", "controls": "carousel-controls", "root": "carousel-root"},
        style={'display': 'flex', 'align-items': 'center', 'height': 60}
    )


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
            miw=600, style={"flex": 1, 'overflow': 'visible'}, p=0
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
            miw=600, style={"flex": 1, 'overflow': 'visible'}, p=0
        )
    ], style={"flex": 1, 'flex-wrap': 'wrap', 'overflow': 'auto'}, align='stretch', w='100%'),
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
