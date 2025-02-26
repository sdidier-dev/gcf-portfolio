import json
import os

import pandas as pd
from dash import Dash, _dash_renderer, Input, Output, State, callback, clientside_callback, no_update, Patch, html
import dash_ag_grid as dag

import dash_mantine_components as dmc
from dash_iconify import DashIconify

from app_config import df_entities, header_template_with_icon, query_to_col, col_to_query

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
    'filter': True, "filterParams": {"maxNumConditions": 1, "buttons": ["reset"]}, "floatingFilter": True,
    'suppressHeaderMenuButton': True,
    "tooltipComponent": "CustomTooltipHeaders",
    "wrapHeaderText": True,
}

dashGridOptions = {
    "headerHeight": 30, "rowHeight": 50,
    'tooltipShowDelay': 500, 'tooltipHideDelay': 15000, 'tooltipInteraction': True,
    "popupParent": {"function": "setPopupsParent()"},  # let the tooltip overflow outside the grid
}


def entities_grid(theme='light'):
    return html.Div([
        dag.AgGrid(
            id={'type': 'grid', 'index': 'entities'},
            rowData=df_entities.to_dict("records"),
            columnDefs=columnDefs,
            defaultColDef=defaultColDef,
            dashGridOptions=dashGridOptions,
            dangerously_allow_code=True,
            className=f"ag-theme-quartz{'' if theme == 'light' else '-dark'}",
            style={"height": '100%', 'box-shadow': 'var(--mantine-shadow-md)'},
        )
    ], style={"flex": 1, 'display': 'flex', 'justify-content': 'center', 'width': '100%', 'maxWidth': 1500,
              'overflow': 'auto'})


# mapping field/queries
query_to_col['entities'] = {
    'entity': {'field': 'Entity', 'type': 'text'},
    'name': {'field': 'Name', 'type': 'text'},
    'country': {'field': 'Country', 'type': 'text'},
    'type': {'field': 'Type', 'type': 'text'},
    'DAE': {'field': 'DAE', 'type': 'bool'},
    'size': {'field': 'Size', 'type': 'text'},
    'sector': {'field': 'Sector', 'type': 'text'},
    'stage': {'field': 'Stage', 'type': 'text'},
    'BM': {'field': 'BM', 'type': 'text'},
    'FAfin': {'field': 'FA Financing', 'type': 'num'},
    'FAnb': {'field': '# Approved', 'type': 'num'},
}
col_to_query['entities'] = {v['field']: k for k, v in query_to_col['entities'].items()}


@callback(
    Output({'type': 'grid', 'index': 'entities'}, "filterModel", allow_duplicate=True),
    Input({'type': 'figure', 'subtype': 'map', 'index': 'entities'}, "clickData"),
    prevent_initial_call=True
)
def entities_map_click(click_data):
    if not click_data:
        return no_update
    selected_country = click_data['points'][0]['customdata'][-1]
    return {'Country': {'filterType': 'text', 'type': 'contains', 'filter': selected_country}}


@callback(
    Output({'type': 'grid', 'index': 'entities'}, "filterModel", allow_duplicate=True),
    Input({'type': 'figure', 'subtype': 'treemap', 'index': 'entities'}, "clickData"),
    State({'type': 'grid', 'index': 'entities-levels-drag'}, "virtualRowData"),
    prevent_initial_call=True
)
def entities_treemap_click(click_data, virtual_data_level):
    if not click_data:
        return no_update

    levels_order = [row['level'] for row in virtual_data_level]
    categories = click_data['points'][0]['id'].split('/')[1:]

    filterModel = {}
    for i, cat in enumerate(categories):
        col = levels_order[i]
        if col == 'DAE':
            filterModel[col] = {'filterType': 'text',
                                'type': 'true' if cat == 'Direct Access Entities (DAE)' else 'false'}
        else:
            filterModel[col] = {'filterType': 'text', 'type': 'contains', 'filter': cat}

    return filterModel
