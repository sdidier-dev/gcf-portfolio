import os

import pandas as pd
from dash import Dash, _dash_renderer, Input, Output, State, callback, clientside_callback, no_update, Patch, html
import dash_ag_grid as dag

import dash_mantine_components as dmc
from dash_iconify import DashIconify

from app_config import df_FA

# sort by ref for the default order in the grid
df_FA.sort_values('Ref #', inplace=True, na_position='last')
# df_FA.columns

# custom header template to add an info icon to emphasize tooltips for that header
header_template_with_icon = """
<div class="ag-cell-label-container" role="presentation">
    <span ref="eMenu" class="ag-header-icon ag-header-cell-menu-button"></span>
    <span ref="eFilterButton" class="ag-header-icon ag-header-cell-filter-button"></span>
    <div ref="eLabel" class="ag-header-cell-label" role="presentation">          
        <span ref="eText" class="ag-header-cell-text" role="columnheader"></span>       
        <span ref="eFilter" class="ag-header-icon ag-filter-icon"></span>
        <span ref="eSortOrder" class="ag-header-icon ag-sort-order ag-hidden"></span>
        <span ref="eSortAsc" class="ag-header-icon ag-sort-ascending-icon ag-hidden"></span>
        <span ref="eSortDesc" class="ag-header-icon ag-sort-descending-icon ag-hidden"></span>
        <span ref="eSortMixed" class="ag-header-icon ag-sort-mixed-icon ag-hidden"></span>
        <span ref="eSortNone" class="ag-header-icon ag-sort-none-icon ag-hidden"></span> 

        &nbsp;<svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 24 24">
        <path fill="var(--ag-header-foreground-color)" d="M12 1.999c5.524 0 10.002 4.478 10.002 10.002c0 5.523-4.478 
        10.001-10.002 10.001S2 17.524 2 12.001C1.999 6.477 6.476 1.999 12 1.999" 
        class="duoicon-secondary-layer" opacity="0.3"/>
        <path fill="var(--ag-header-foreground-color)" d="M12.001 6.5a1.252 1.252 0 1 0 .002 2.503A1.252 1.252 0 0 0 
        12 6.5zm-.005 3.749a1 1 0 0 0-.992.885l-.007.116l.004 5.502l.006.117a1 1 0 0 0 1.987-.002L13 
        16.75l-.004-5.501l-.007-.117a1 1 0 0 0-.994-.882z" class="duoicon-primary-layer"/></svg>

    </div>
</div>
"""

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
        "valueFormatter": {"function": "'B.' + params.value"},

    },
    {
        'field': 'FA Financing', 'headerTooltip': 'Funded Activities Financing', 'cellStyle': {'textAlign': 'right'},
        "valueFormatter": {"function": "d3.format('$.4s')(params.value)"},
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
], style={"flex": 1, 'display': 'flex', 'justify-content': 'center', 'width': '100%', 'overflow': 'auto'})


@callback(
    Output("fa-grid", "className"),
    Input("color-scheme-switch", "checked"),
)
def fa_grid_switch_theme(checked):
    return "ag-theme-quartz" if checked else "ag-theme-quartz-dark"
