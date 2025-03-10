import os

from dash import Dash, _dash_renderer, Input, Output, State, callback, clientside_callback, Patch, ctx, ALL
import dash_ag_grid as dag

import dash_mantine_components as dmc
from dash_iconify import DashIconify

import pandas as pd
from dash import Dash, html, Input, Output, register_page, clientside_callback, dcc, callback, State
import pages.FA.components as components
from app_config import text_carousel

register_page(__name__, path="/funded-activities", title="Funded Activities",
              description="The Funded Activities dashboard shows the approved projects "
                          "and the distribution of the projects by categories.",
              )

layout = dmc.Stack(id='fa-container', w='100%', style={"flex": 1}, align='center')


# we use a callback to render the children to be able to provide the theme before they render
# to avoid flickering at init and when switching dashboard
@callback(
    Output('fa-container', "children"),
    Input('fa-container', "id"),
    State("color-scheme-switch", "checked"),
)
def render_children(_, checked):
    theme = 'light' if checked else 'dark'
    return [
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
                        styles={"input": {'color': 'var(--primary)', 'fontSize': 20, 'fontWeight': 'bold',
                                          'textDecoration': 'underline', 'cursor': 'pointer'},
                                "dropdown": {'border': '1px solid var(--primary)'},
                                "option": {'fontSize': 14, 'fontWeight': 'bold'}},
                        comboboxProps={"transitionProps": {"transition": "scale-y", "duration": 200}},
                    ),
                ], className='card-header', fz=20, h=40,
                    style={'gap': 5, 'borderRadius': '8px 8px 0px 0px'}),
                dmc.Divider(),

                components.fa_timeline(theme)

            ], withBorder=True, shadow="sm", radius='md',
                p=0, mt=10,  # NOTE: add a margin to allow the overflow of the text Carousel control
                miw=500, mih=400, style={"flex": 2, 'overflow': 'visible'}
            ),
            dmc.Card([
                dmc.Center([
                    "Projects",
                    text_carousel(["Financing", "Number"], "fa-bar-carousel"),
                    "Distribution by Categories",
                ], className='card-header', fz=20, h=40,
                    style={'gap': 5, 'borderRadius': '8px 8px 0px 0px'}),
                dmc.Divider(),

                components.fa_bar(theme)

            ], withBorder=True, shadow="sm", radius='md',
                p=0, mt=10,  # NOTE: add a margin to allow the overflow of the text Carousel control
                miw=600, mih=400, style={"flex": 2, 'overflow': 'visible'}
            ),
            dmc.Card([
                dmc.Center([
                    "Projects Financing Distribution",
                ], className='card-header', fz=20, h=40,
                    style={'gap': 5, 'borderRadius': '8px 8px 0px 0px'}),
                dmc.Divider(),

                components.fa_histogram(theme)

            ], withBorder=True, shadow="sm", radius='md',
                p=0, mt=10,  # NOTE: add a margin to allow the overflow of the text Carousel control
                miw=400, mih=400, style={"flex": 1, 'overflow': 'visible'}
            ),

        ], style={"flex": 1, 'flexWrap': 'wrap', 'overflow': 'auto'}, align='stretch', w='100%'
        ),
        dmc.Group([
            dmc.Button("Reset Filters", id={"type": "reset-filter-btn", "index": 'fa'},
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

        components.fa_grid(theme)

    ]
