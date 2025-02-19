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
                dmc.Select(
                    id="fa-timeline-select",
                    data=[v for v in components.cat_cols.keys()],
                    value="Theme",
                    size="xs", w=200,
                    allowDeselect=False, checkIconPosition="right",
                    variant='unstyled',
                    leftSection=DashIconify(icon="mynaui:chevron-up-down", color='var(--primary)'),
                    leftSectionWidth=15,
                    rightSection=' ', rightSectionWidth=0,
                    leftSectionPointerEvents="none", rightSectionPointerEvents="none",
                    ml=-5,  # add a negative margin left to remove the gap
                    styles={"input": {'color': 'var(--primary)', 'font-size': 20, 'font-weight': 'bold',
                                      'text-decoration': 'underline', 'cursor': 'pointer'},
                            "dropdown": {'border': '1px solid var(--primary)'},
                            "option": {'font-size': 14, 'font-weight': 'bold'}},
                    comboboxProps={"transitionProps": {"transition": "scale-y", "duration": 200}},
                ),
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
        dmc.Button("Reset Grid Filters", id='fa-grid-reset-btn', variant="outline", color='var(--primary)',
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

    components.FA_grid

], w='100%', style={"flex": 1}, align='center')
