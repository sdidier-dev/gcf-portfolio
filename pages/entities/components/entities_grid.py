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

total_cols = ['FA Financing', '# Approved']
totals = df_entities[total_cols].sum()

columnDefs = [
    {'field': 'Entity', 'tooltipField': 'Entity', 'width': 120,
     # special styling for the bottom pinned row 'total' cell
     'colSpan': {"function": "params.data['Entity'] === 'TOTAL' ? 9 : 1"},
     'cellStyle': {"function": "params.value == 'TOTAL' && {'display': 'flex', 'justifyContent': 'flex-end'}"},
     },
    {'field': 'Name', 'tooltipField': 'Name', 'width': 300},
    {'field': 'Country',
     "cellRenderer": "CountriesCell",
     'tooltipField': 'Country', "tooltipComponent": "CustomTooltipCountries",
     'cellStyle': {'display': 'flex', 'alignItems': 'center'}, 'width': 150
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
          "cellRenderer": "InternalLinkCell", "width": 140
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
    "headerHeight": 30, 'tooltipShowDelay': 500, 'tooltipHideDelay': 15000, 'tooltipInteraction': True,
    "popupParent": {"function": "setPopupsParent()"},  # let the tooltip overflow outside the grid
    "pinnedBottomRowData": [{"Entity": "TOTAL", **{col: totals[col] for col in total_cols}}]
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
            style={"height": '100%'},
        )
    ], style={"flex": 1, 'display': 'flex', 'justifyContent': 'center', 'width': '100%', 'maxWidth': 1500,
              'overflow': 'auto', 'boxShadow': 'var(--mantine-shadow-md)'})


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
    Output({'type': 'grid', 'index': 'entities'}, "dashGridOptions"),
    Input({'type': 'grid', 'index': 'entities'}, "virtualRowData"),
)
def row_pinning_bottom(virtual_data):
    if not virtual_data:
        return no_update

    cols = ['FA Financing', '# Approved']
    dff = pd.DataFrame(virtual_data, columns=cols)
    totals = dff[cols].sum()

    grid_option_patch = Patch()
    grid_option_patch["pinnedBottomRowData"] = [{"Entity": "TOTAL", **{col: totals[col] for col in cols}}]
    return grid_option_patch


@callback(
    Output("url-location", "pathname", allow_duplicate=True),
    Output("url-location", "search", allow_duplicate=True),
    Output("url-location", "refresh", allow_duplicate=True),
    Input({'type': 'grid', 'index': 'entities'}, "cellRendererData"),
    State({'type': 'grid', 'index': 'entities'}, "virtualRowData"),
    prevent_initial_call=True
)
def cell_icon_click(click_data, virtual_data):
    if not click_data:
        return no_update

    # Note: DASH_URL_BASE_PATHNAME needs a trailing '/', so must be removed from the subdomains below
    base_path = os.getenv('DASH_URL_BASE_PATHNAME', '/')

    if click_data['value'] == 'TOTAL':
        entities = [row['Entity'].replace(' ', '_') for row in virtual_data]
        query = f"?{col_to_query['fa']['Entity']}={'+'.join(entities)}"
    else:
        query = f"?{col_to_query['fa']['Entity']}={click_data['value'].replace(' ', '_')}"
    return base_path + "funded-activities", query, 'callback-nav'


@callback(
    Output({'type': 'grid', 'index': 'entities'}, "filterModel", allow_duplicate=True),
    Input({'type': 'figure', 'subtype': 'map', 'index': 'entities'}, "clickData"),
    State({'type': 'grid', 'index': 'entities'}, "filterModel"),
    prevent_initial_call=True
)
def entities_map_click(click_data, filter_model):
    if not click_data:
        return no_update

    selected_country = click_data['points'][0]['customdata'][-1]
    filter_model['Country'] = {'filterType': 'text', 'type': 'contains', 'filter': selected_country}
    return filter_model


@callback(
    Output({'type': 'grid', 'index': 'entities'}, "filterModel", allow_duplicate=True),
    Input({'type': 'figure', 'subtype': 'treemap', 'index': 'entities'}, "clickData"),
    State({'type': 'grid', 'index': 'entities-levels-drag'}, "virtualRowData"),
    State({'type': 'grid', 'index': 'entities'}, "filterModel"),
    prevent_initial_call=True
)
def entities_treemap_click(click_data, virtual_data_level, filter_model):
    if not click_data:
        return no_update

    levels_order = [row['level'] for row in virtual_data_level]
    categories = click_data['points'][0]['id'].split('/')[1:]

    for i, cat in enumerate(categories):
        col = levels_order[i]
        if col == 'DAE':
            filter_model[col] = {'filterType': 'text',
                                 'type': 'true' if cat == 'Direct Access Entities (DAE)' else 'false'}
        else:
            filter_model[col] = {'filterType': 'text', 'type': 'contains', 'filter': cat}

    return filter_model
