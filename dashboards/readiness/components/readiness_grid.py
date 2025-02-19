import json
import os

import pandas as pd
from dash import Dash, _dash_renderer, Input, Output, State, callback, clientside_callback, no_update, Patch, html
import dash_ag_grid as dag

import dash_mantine_components as dmc
from dash_iconify import DashIconify

from app_config import df_readiness, header_template_with_icon

# sort by ref for the default order in the grid
df_readiness.sort_values('Ref #', inplace=True, na_position='last')

financing_header_tooltip = '''
  The amount of GCF funding allocated to each country  
  is an estimate based on the best information available  
  to the Secretariat. Unless allocation information for  
  projects are provided, funding amounts are evenly  
  distributed to each targeted country. These estimates  
  are updated once expenditure information is received  
  for each project.
'''

ref_col = {'field': 'Ref #'}
project_col = {
    'field': 'Project Title', 'tooltipField': 'Project Title',
    'width': 300
}
activity_col = {
    'field': 'Activity', 'tooltipField': 'Activity',
    'width': 270
}
nap_col = {
    'field': 'NAP', "cellClass": 'center-flex-cell', "cellRenderer": "CheckBool",
    "headerComponentParams": {"template": header_template_with_icon},
    'headerTooltip': 'National Adaptation Plans',
    'width': 100
}
partner_col = {'field': 'Delivery Partner', 'tooltipField': 'Partner Name', 'width': 300}
country_col = {
    'field': 'Country', "cellRenderer": "CountriesCell",
    'tooltipField': 'Country', "tooltipComponent": "CustomTooltipCountries",
    'cellStyle': {'display': 'flex', 'align-items': 'center'}

}
region_col = {'field': 'Region', 'width': 150}
sids_col = {
    'field': 'SIDS', "cellClass": 'center-flex-cell', "cellRenderer": "CheckBool",
    "headerComponentParams": {"template": header_template_with_icon},
    'headerTooltip': 'Small Island Developing States',
    'width': 100
}
ldc_col = {
    'field': 'LDC', "cellClass": 'center-flex-cell', "cellRenderer": "CheckBool",
    "headerComponentParams": {"template": header_template_with_icon},
    'headerTooltip': 'Least Developed Countries',
    'width': 100
}
as_col = {
    'field': 'AS', "cellClass": 'center-flex-cell', "cellRenderer": "CheckBool",
    "headerComponentParams": {"template": header_template_with_icon},
    'headerTooltip': 'African States',
    'width': 100
}

status_col = {'field': 'Status', "cellRenderer": "CustomReadinessStatusCell",
              "cellClass": 'center-flex-cell', "pinned": "right"}

date_obj = "d3.timeParse('%Y-%m-%dT%H:%M:%S')(params.data['Approved Date'])"

approved_date_col = {
    'field': 'Approved Date str', 'headerName': 'Approved Date', 'cellStyle': {'textAlign': 'center'},
    "valueFormatter": {"function": f"d3.timeFormat('%b %d, %Y')({date_obj})"},
    'width': 200, "pinned": "right"
}
financing_col = {
    'field': 'Financing', 'cellStyle': {'textAlign': 'right'},
    "valueFormatter": {"function": "d3.format('$.4s')(params.value)"},
    'width': 100, "pinned": "right",
    "headerComponentParams": {"template": header_template_with_icon},
    'headerTooltip': financing_header_tooltip
}

columnDefs = [
    {
        'headerName': 'Project', "headerClass": 'center-aligned-header', "suppressStickyLabel": True,
        'children': [
            ref_col,
            project_col,
            activity_col,
            nap_col,
        ]
    },
    partner_col,
    country_col,
    region_col,
    {
        'headerName': 'Priority States', "headerClass": 'center-aligned-header', "suppressStickyLabel": True,
        "headerGroupComponentParams": {"template": header_template_with_icon},
        'headerTooltip': 'Most climate vulnerable countries',
        'children': [
            sids_col,
            ldc_col,
            as_col,
        ]
    },
    status_col,
    approved_date_col,
    financing_col
]

defaultColDef = {
    "headerClass": 'center-aligned-header',
    'filter': True, "filterParams": {"buttons": ["reset"]}, "floatingFilter": True,
    'suppressHeaderMenuButton': True,
    "tooltipComponent": "CustomTooltipHeaders",
}

dashGridOptions = {
    "headerHeight": 30,
    "rowHeight": 50,
    'tooltipShowDelay': 500,
    'tooltipHideDelay': 15000,
    'tooltipInteraction': True,
    "popupParent": {"function": "setPopupsParent()"}
}

readiness_grid = html.Div([
    dag.AgGrid(
        id="readiness-grid",
        rowData=df_readiness.to_dict("records"),
        columnDefs=columnDefs,
        defaultColDef=defaultColDef,
        dashGridOptions=dashGridOptions,
        dangerously_allow_code=True,
        columnSize="autoSize",
        columnSizeOptions={'keys': [
            'Ref #', 'Delivery Partner', 'Region', 'SIDS', 'LDC', 'NAP', 'Status', 'Approved Date', 'Financing'
        ]},
        style={
            "height": '100%',
            "max-width": 2225,
            'box-shadow': 'var(--mantine-shadow-md)',
        },
    )
], style={"flex": 1, 'display': 'flex', 'justify-content': 'center', 'width': '100%', 'overflow': 'auto'})


@callback(
    Output("readiness-grid", "filterModel"),
    Input("readiness-grid", "id"),
    State("readiness-grid-filter-state-store", "data"),
)
def apply_filter(_, temp_filter):
    # apply existing filter from the store once the grid is ready,
    return json.loads(temp_filter) if temp_filter else no_update


@callback(
    Output("readiness-grid-filter-state-store", "data", allow_duplicate=True),
    Input("readiness-grid", "filterModel"),
    prevent_initial_call=True
)
def save_filter(filter_model):
    # save the current filter state to reapply it when switching tabs
    return json.dumps(filter_model)


@callback(
    Output("readiness-grid", "filterModel", allow_duplicate=True),
    Input("readiness-grid-reset-btn", "n_clicks"),
    prevent_initial_call=True
)
def reset_filter(_):
    return {}


@callback(
    Output("readiness-grid", "className"),
    Input("color-scheme-switch", "checked"),
)
def readiness_grid_switch_theme(checked):
    return "ag-theme-quartz" if checked else "ag-theme-quartz-dark"
