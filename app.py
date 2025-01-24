import json
import os
from pprint import pprint

from dash import Dash, dcc, html, Input, Output, State, callback, no_update, clientside_callback, _dash_renderer
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from dashboards import *

_dash_renderer._set_react_version("18.2.0")
dmc.add_figure_templates()

app = Dash(external_stylesheets=dmc.styles.ALL, suppress_callback_exceptions=True)

server = app.server

dashboard_layouts = {
    "countries": countries_dashboard,
    "readiness": readiness_dashboard,
    "project": projects_dashboard,
    "entities": entities_dashboard
}

header = dmc.Group(
    [
        dmc.Anchor(
            [DashIconify(icon="cil:graph", width=25), dmc.Text("GREEN CLIMATE FUND", fw='bold', variant="gradient")],
            href="https://www.greenclimate.fund/", target="_blank", underline=False, c='var(--primary)',
            display='flex', style={'gap': 5}
        ),

        dmc.Title("GCF Projects Portfolio", c="var(--primary)"),

        dmc.Group([
            dmc.Switch(
                id='color-scheme-switch',
                offLabel=DashIconify(icon="radix-icons:moon", width=20),
                onLabel=DashIconify(icon="radix-icons:sun", width=20),
                size="lg", persistence=True, color='var(--primary)',
                styles={"track": {'border': "2px solid var(--primary)"}},
            ),
            dmc.Anchor(
                DashIconify(icon="mdi:github", width=34), c='var(--primary)',
                href="https://github.com/sdidier-dev/figure-friday", target="_blank", display='flex'
            ),

        ])
    ],
    justify='space-between', pb=10,
    style={'border-bottom': "2px solid var(--primary)"}
)

app.layout = dmc.MantineProvider(
    [
        dmc.Stack([
            header,

            dmc.SegmentedControl(
                id="dashboard-segmented-control",
                data=[
                    {"value": "countries", "label": "COUNTRIES"},
                    {"value": "readiness", "label": "READINESS"},
                    {"value": "project", "label": "PROJECTS"},
                    {"value": "entities", "label": "ENTITIES"},
                ],
                value="readiness",
                color='var(--primary)', mt=10,
                style={'box-shadow': 'var(--mantine-shadow-md)'},
            ),

            dmc.Flex(id='dashboard-container', style={"flex": 1})

        ], h='100vh', p=10, style={'gap': 0})
    ],
    id="mantine-provider",
    theme={
        "primaryColor": "teal",
        "defaultGradient": {
            "from": 'teal',
            "to": 'blue',
            "deg": 45,
        },
        'spacing': {'md': '10px'},

    }

)


@callback(
    Output("mantine-provider", "forceColorScheme"),
    Input("color-scheme-switch", "checked"),
)
def switch_theme(checked):
    return "light" if checked else "dark"


@callback(
    Output("dashboard-container", "children"),
    Input("dashboard-segmented-control", "value")
)
def switch_dashboard(value):
    return dashboard_layouts[value]


if __name__ == '__main__':
    app.run_server(debug=True)
