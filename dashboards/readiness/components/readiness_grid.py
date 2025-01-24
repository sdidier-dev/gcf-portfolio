import os

import pandas as pd
from dash import Dash, _dash_renderer, Input, Output, State, callback, clientside_callback, no_update, Patch, html
import dash_ag_grid as dag

import dash_mantine_components as dmc
from dash_iconify import DashIconify

from app_config import df_readiness

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
partner_col = {'field': 'Delivery Partner'}
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

date_obj = "d3.timeParse('%Y-%m-%d')(params.data['Approved Date'])"
approved_date_col = {
    'field': 'Approved Date', 'cellStyle': {'textAlign': 'center'},
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
    Output("readiness-grid", "className"),
    Input("color-scheme-switch", "checked"),
)
def readiness_grid_switch_theme(checked):
    return "ag-theme-quartz" if checked else "ag-theme-quartz-dark"
