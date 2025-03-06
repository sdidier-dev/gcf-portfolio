import json
import os
from pprint import pprint
from urllib.parse import urlparse, parse_qs

from dash import Dash, dcc, Input, Output, callback, _dash_renderer, Patch, ctx, ALL, page_container, page_registry, \
    no_update, html, State, MATCH
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from dotenv import load_dotenv
import plotly.io as pio

from app_config import parse_as_number, query_to_filter, filter_to_query, query_to_col, col_to_query
import importlib

# load env variable to know if the app is local or deployed
load_dotenv()

_dash_renderer._set_react_version("18.2.0")
dmc.add_figure_templates()

app = Dash(
    use_pages=True,
    external_stylesheets=dmc.styles.ALL,
    suppress_callback_exceptions=True
)

server = app.server
page_container.style = {"flex": 1}

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
    style={'borderBottom': "2px solid var(--primary)"}
)

app.layout = dmc.MantineProvider(
    [
        dmc.Stack([
            header,

            dmc.SegmentedControl(
                id="dashboard-segmented-control",
                data=[
                    {"value": "/countries", "label": "COUNTRIES"},
                    {"value": "/readiness", "label": "READINESS PROGRAMMES"},
                    {"value": "/funded-activities", "label": "FUNDED ACTIVITIES"},
                    {"value": "/entities", "label": "ENTITIES"},
                ],
                value="/countries",
                color='var(--primary)', mt=10,
                style={'boxShadow': 'var(--mantine-shadow-md)', 'flexWrap': 'wrap', 'overflow': 'auto',
                       'minHeight': 50},
            ),

            page_container

        ], h='100vh', p=10, style={'gap': 0}),

        dcc.Location(id='url-location',
                     # refresh='callback-nav'
                     ),
        # keep the queries corresponding to grid filter models to reapply them when switching tabs
        dcc.Store(id="queries-store",
                  # storage_type='session',  # cleared when closing the browser
                  data={"/countries": '', "/readiness": '', "/funded-activities": '', "/entities": ''}
                  ),
    ],
    id="mantine-provider",
    theme={
        "primaryColor": "teal",
        "defaultGradient": {"from": 'teal', "to": 'blue', "deg": 45},
        'spacing': {'md': '10px'},
    }
)


@callback(
    Output("dashboard-segmented-control", "value"),
    Output("url-location", "pathname"),
    Output("url-location", "search"),
    Output("url-location", "refresh"),
    Input("dashboard-segmented-control", "value"),
    Input("url-location", "pathname"),
    State("queries-store", "data"),
    prevent_initial_call=True
)
def switch_dashboard(value, path, queries_store):
    if ctx.triggered_id == 'dashboard-segmented-control':
        # DASH_URL_BASE_PATHNAME needs a trailing '/', so must be removed from value
        print('before ', value, path, queries_store, os.getenv('DASH_URL_BASE_PATHNAME', '/'))
        path = os.getenv('DASH_URL_BASE_PATHNAME', '/') + value[1:]
        print('after ', value, path, queries_store)
        # 'callback-nav' to only refresh page_container
        return value, path, queries_store[value], 'callback-nav'
    else:
        # only update the segmented-control value when providing the path
        return path, no_update, no_update, no_update


# Query tests locally
# http://127.0.0.1:8050/countries?country=a+b&country=c&countryOperator=AND&SIDS=true&RPnb=10-20
# http://127.0.0.1:8050/readiness?ref=a&project=a&NAP=true&status=dis
@callback(
    Output("queries-store", "data"),
    Input("url-location", "search"),
    State("url-location", "pathname"),
    State("queries-store", "data"),
    prevent_initial_call=True
)
def store_query(query, path, queries_store):
    queries_store[path] = query
    return queries_store


# # Note: using grid ids as input, the callback will be triggered once the grid is loaded and ready
# # thus triggered at init, switching dashboards and modifying the URL query manually as it will rerender the page
@callback(
    Output({"type": "grid", "index": MATCH}, "filterModel"),
    Input({"type": "grid", "index": MATCH}, "id"),
    State("url-location", "search"),
)
def update_filter_from_query(grid_id, query):
    return query_to_filter(query, query_to_col[grid_id['index']]) if grid_id['index'] in query_to_col else no_update


@callback(
    Output("url-location", "search", allow_duplicate=True),
    Output("url-location", "refresh", allow_duplicate=True),
    Input({"type": "grid", "index": ALL}, "filterModel"),
    prevent_initial_call=True
)
def update_query_from_filter(filter_models):
    if not filter_models:
        return no_update, no_update

    # update URL query without refreshing the page only with the first non-empty grid filter model
    # (only one should be used per page) and remove the query when there is no filter_model, like using reset btn
    for filter_model in filter_models:
        if filter_model and ctx.triggered_id['index'] in col_to_query.keys():
            return filter_to_query(filter_model, col_to_query[ctx.triggered_id['index']]), False
    return '', False


@callback(
    Output({"type": "grid", "index": MATCH}, "filterModel", allow_duplicate=True),
    Input({"type": "reset-filter-btn", "index": MATCH}, "n_clicks"),
    prevent_initial_call=True
)
def reset_grid_filter(_):
    return {}


@callback(
    Output("mantine-provider", "forceColorScheme"),
    Output({'type': 'grid', 'index': ALL}, "className"),
    Output({'type': 'figure', 'subtype': ALL, 'index': ALL}, "figure"),
    Input("color-scheme-switch", "checked"),
)
def switch_theme(checked):
    main_layout_theme = "light" if checked else "dark"

    grids_theme = ["ag-theme-quartz" if checked else "ag-theme-quartz-dark"] * len(ctx.outputs_list[1])

    fig_patch_list = []
    for fig in ctx.outputs_list[2]:
        fig_patch = Patch()
        fig_patch["layout"]["template"] = pio.templates[f"mantine_{'light' if checked else 'dark'}"]

        if fig['id']['subtype'] == 'map':
            fig_patch["layout"]['geo']['landcolor'] = '#f1f3f5' if checked else '#1f1f1f'
        if fig['id']['subtype'] == 'treemap':
            fig_patch["data"][0]["root"]["color"] = "rgba(0,0,0,0.1)" if checked else "rgba(255,255,255,0.1)"

        fig_patch_list.append(fig_patch)

    return main_layout_theme, grids_theme, fig_patch_list


if __name__ == '__main__':
    app.run(debug=True)
