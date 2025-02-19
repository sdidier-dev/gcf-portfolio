import json
import os

import pandas as pd
from dash import Dash, _dash_renderer, Input, Output, State, callback, clientside_callback, no_update, Patch, html
import dash_ag_grid as dag

import dash_mantine_components as dmc
from dash_iconify import DashIconify

from app_config import df_entities, header_template_with_icon

# sort by ref for the default order in the grid
df_entities.sort_values('Entity', inplace=True, na_position='last')

columnDefs = [
    {'field': 'Entity', 'tooltipField': 'Entity', 'width': 120},
    {'field': 'Name', 'tooltipField': 'Name', 'width': 300},
    {'field': 'Country',
     "cellRenderer": "CountriesCell",
     'tooltipField': 'Country', "tooltipComponent": "CustomTooltipCountries",
     'cellStyle': {'display': 'flex', 'align-items': 'center'}, 'width': 150
     },
    {'headerName': 'Details', "headerClass": 'center-aligned-header', "suppressStickyLabel": True,
     'children': [
         {'field': 'Type', "cellClass": 'center-flex-cell', 'width': 100},
         {'field': 'DAE', "cellClass": 'center-flex-cell', "cellRenderer": "CheckBool",
          "headerComponentParams": {"template": header_template_with_icon},
          'headerTooltip': 'Direct Access Entities', 'width': 100
          },
         {'field': 'Size', "cellClass": 'center-flex-cell', 'width': 100},
         {'field': 'Sector', "cellClass": 'center-flex-cell', 'width': 100},
     ]},
    {'headerName': 'Accreditation', "headerClass": 'center-aligned-header', "suppressStickyLabel": True,
     'children': [
         {'field': 'Stage', "cellClass": 'center-flex-cell', 'width': 130},
         {'field': 'BM', "cellClass": 'center-flex-cell', 'width': 100,
          "headerComponentParams": {"template": header_template_with_icon},
          'headerTooltip': 'Board Meeting',
          "valueFormatter": {"function": "'B.' + params.value"}
          },
     ]},
    {'headerName': 'Funded Activities', "headerClass": 'center-aligned-header', "suppressStickyLabel": True,
     'children': [
         {'field': 'FA Financing', 'headerName': 'Financing', 'cellStyle': {'textAlign': 'right'},
          "valueFormatter": {"function": "formatMoneyNumberSI(params.value)"},
          "width": 140
          },
         {'field': '# Approved', 'headerName': 'Nb of Projects', "cellClass": 'center-flex-cell',
          "cellRenderer": "CustomButtonCell", "width": 140
          }
     ]},
]

defaultColDef = {
    "headerClass": 'center-aligned-header',
    'filter': True, "filterParams": {"buttons": ["reset"]}, "floatingFilter": True,
    'suppressHeaderMenuButton': True,
    "tooltipComponent": "CustomTooltipHeaders",
    "wrapHeaderText": True,
}

dashGridOptions = {
    "headerHeight": 30, "rowHeight": 50,
    'tooltipShowDelay': 500, 'tooltipHideDelay': 15000, 'tooltipInteraction': True,
    "popupParent": {"function": "setPopupsParent()"},  # let the tooltip overflow outside the grid
}

entities_grid = html.Div([
    dag.AgGrid(
        id="entities-grid",
        rowData=df_entities.to_dict("records"),
        columnDefs=columnDefs,
        defaultColDef=defaultColDef,
        dashGridOptions=dashGridOptions,
        dangerously_allow_code=True,
        style={"height": '100%', 'box-shadow': 'var(--mantine-shadow-md)'},
    )
], style={"flex": 1, 'display': 'flex', 'justify-content': 'center', 'width': '100%', 'maxWidth': 1500,
          'overflow': 'auto'})


@callback(
    Output("entities-grid", "filterModel", allow_duplicate=True),
    Input("entities-treemap-graph", "clickData"),
    State("entities-levels-drag-grid", "virtualRowData"),
    prevent_initial_call=True
)
def treemap_click(click_data, virtual_data_level):
    if not click_data:
        return no_update

    levels_order = [row['level'] for row in virtual_data_level]
    categories = click_data['points'][0]['id'].split('/')[1:]

    # {'DAE': {'filterType': 'text', 'type': 'true'},
    # 'Sector': {'filterType': 'text', 'type': 'contains', 'filter': 'Public'}}
    filterModel = {}
    for i, cat in enumerate(categories):
        col = levels_order[i]
        if col == 'DAE':
            filterModel[col] = {'filterType': 'text',
                                'type': 'true' if cat == 'Direct Access Entities (DAE)' else 'false'}
        else:
            filterModel[col] = {'filterType': 'text', 'type': 'contains', 'filter': cat}

    return filterModel


@callback(
    Output("entities-grid", "filterModel", allow_duplicate=True),
    Input("entities-map", "clickData"),
    prevent_initial_call=True
)
def map_click(click_data):
    if not click_data:
        return no_update
    selected_country = click_data['points'][0]['customdata'][-1]
    return {'Country': {'filterType': 'text', 'type': 'contains', 'filter': selected_country}}


@callback(
    Output("entities-grid", "filterModel"),
    Input("entities-grid", "id"),
    State("entities-grid-filter-state-store", "data"),
)
def apply_filter(_, temp_filter):
    # apply existing filter from the store once the grid is ready,
    return json.loads(temp_filter) if temp_filter else no_update


@callback(
    Output("entities-grid-filter-state-store", "data", allow_duplicate=True),
    Input("entities-grid", "filterModel"),
    prevent_initial_call=True
)
def save_filter(filter_model):
    # save the current filter state to reapply it when switching tabs
    return json.dumps(filter_model)


@callback(
    Output("entities-grid", "filterModel", allow_duplicate=True),
    Input("entities-grid-reset-btn", "n_clicks"),
    prevent_initial_call=True
)
def reset_filter(_):
    return {}


@callback(
    Output("entities-grid", "className"),
    Input("color-scheme-switch", "checked"),
)
def entities_grid_switch_theme(checked):
    return "ag-theme-quartz" if checked else "ag-theme-quartz-dark"
