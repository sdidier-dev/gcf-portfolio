import json
import os

import pandas as pd
from dash import Dash, _dash_renderer, Input, Output, State, callback, clientside_callback, no_update, Patch, html
import dash_ag_grid as dag

import dash_mantine_components as dmc
from dash_iconify import DashIconify

from app_config import df_FA, header_template_with_icon

# sort by ref for the default order in the grid
df_FA.sort_values('Ref #', inplace=True, na_position='last')

financing_header_tooltip = '''
  The amount of GCF funding allocated to each country  
  is an estimate based on the best information available  
  to the Secretariat. Unless allocation information for  
  projects are provided, funding amounts are evenly  
  distributed to each targeted country. These estimates  
  are updated once expenditure information is received  
  for each project.
'''

columnDefs = [
    {
        'headerName': 'Project', "headerClass": 'center-aligned-header', "suppressStickyLabel": True,
        'children': [
            {'field': 'Ref #', 'headerName': 'Reference', "cellClass": 'center-flex-cell', 'width': 100},
            {'field': 'Modality', "cellClass": 'center-flex-cell', 'width': 100},
            {'field': 'Project Name', 'tooltipField': 'Project Name', 'width': 300},
            {'field': 'Theme', "cellClass": 'center-flex-cell', 'width': 130},
            {'field': 'Sector', "cellClass": 'center-flex-cell', 'width': 130},
            {'field': 'Project Size', "cellClass": 'center-flex-cell', 'width': 130},
            {'field': 'ESS Category', 'headerTooltip': 'Environmental and Social Safeguards Category', 'width': 150},
        ]
    },

    {
        'field': 'Countries',
        "cellRenderer": "CountriesCell",
        'tooltipField': 'Countries', "tooltipComponent": "CustomTooltipCountries",
        'cellStyle': {'display': 'flex', 'align-items': 'center'}, 'width': 300
    },
    {'field': 'Priority State', "cellClass": 'center-flex-cell', "cellRenderer": "CheckBool", 'width': 100},
    {'field': 'Entity', 'tooltipField': 'Entity Name'},
    {
        'field': 'BM', 'headerName': 'Board Meeting', "cellClass": 'center-flex-cell', "pinned": "right", 'width': 100,
        "valueFormatter": {"function": "'B.' + params.value"}
    },
    {
        'field': 'FA Financing', 'headerTooltip': 'Funded Activities Financing', 'cellStyle': {'textAlign': 'right'},
        "valueFormatter": {"function": "formatMoneyNumberSI(params.value)"},
        "pinned": "right", 'width': 100
    },
]

defaultColDef = {
    "headerClass": 'center-aligned-header',
    'filter': True, "filterParams": {"buttons": ["reset"]}, "floatingFilter": True,
    'suppressHeaderMenuButton': True,
    "tooltipComponent": "CustomTooltipHeaders",
    "wrapHeaderText": True,
}

dashGridOptions = {
    "headerHeight": 30,
    "rowHeight": 50,
    'tooltipShowDelay': 500, 'tooltipHideDelay': 15000, 'tooltipInteraction': True,
    "popupParent": {"function": "setPopupsParent()"},  # let the tooltip overflow outside the grid
}

FA_grid = html.Div([
    dag.AgGrid(
        id="fa-grid",
        rowData=df_FA.to_dict("records"),
        columnDefs=columnDefs,
        defaultColDef=defaultColDef,
        dashGridOptions=dashGridOptions,
        dangerously_allow_code=True,
        style={
            "height": '100%',
            # "max-width": 2225,
            'box-shadow': 'var(--mantine-shadow-md)',
        },
    )
], style={"flex": 1, 'display': 'flex', 'justify-content': 'center', 'width': '100%', 'maxWidth': 1800,
          'overflow': 'auto'})


@callback(
    Output("fa-grid", "filterModel"),
    Input("fa-grid", "id"),
    State("fa-grid-filter-state-store", "data"),
)
def apply_filter(_, temp_filter):
    # apply existing filter from the store once the grid is ready,
    return json.loads(temp_filter) if temp_filter else no_update


@callback(
    Output("fa-grid-filter-state-store", "data", allow_duplicate=True),
    Input("fa-grid", "filterModel"),
    prevent_initial_call=True
)
def save_filter(filter_model):
    # save the current filter state to reapply it when switching tabs
    return json.dumps(filter_model)


@callback(
    Output("fa-grid", "filterModel", allow_duplicate=True),
    Input("fa-grid-reset-btn", "n_clicks"),
    prevent_initial_call=True
)
def reset_filter(_):
    return {}


@callback(
    Output("fa-grid", "className"),
    Input("color-scheme-switch", "checked"),
)
def fa_grid_switch_theme(checked):
    return "ag-theme-quartz" if checked else "ag-theme-quartz-dark"
