import json
import os

import pandas as pd
from dash import Dash, _dash_renderer, Input, Output, State, callback, clientside_callback, no_update, Patch, html
import dash_ag_grid as dag

import dash_mantine_components as dmc
from dash_iconify import DashIconify

from app_config import df_countries

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
    {'field': 'Country Name', 'headerName': 'Country',
     "headerComponentParams": {"template": header_template_with_icon},
     'headerTooltip': '''
        <u>**[Non-annex 1 countries:](https://unfccc.int/parties-observers)**</u>  
        Countries **especially vulnerable** to the adverse impacts of  
        climate change that are eligible to receive GCF funding.
        ''',
     "cellRenderer": "CountriesCell",
     # special styling for the bottom pinned row 'total' cell and center flags
     'colSpan': {"function": "params.data['Country Name'] === 'TOTAL' ? 5 : 1"},
     'cellStyle': {"function": "params.value == 'TOTAL' ? {'text-align': 'end'} "
                               ": {'display': 'flex', 'align-items': 'center', 'gap': 10,}"}
     },
    {'field': 'Region'},
    {'headerName': 'Priority States', "headerClass": 'center-aligned-header', "suppressStickyLabel": True,
     "headerGroupComponentParams": {"template": header_template_with_icon},
     'headerTooltip': 'Most climate vulnerable countries',

     'children': [
         {'field': 'SIDS', "cellClass": 'center-flex-cell', "cellRenderer": "CheckBool",
          "headerComponentParams": {"template": header_template_with_icon},
          'headerTooltip': 'Small Island Developing States'
          },
         {'field': 'LDC', "cellClass": 'center-flex-cell', "cellRenderer": "CheckBool",
          "headerComponentParams": {"template": header_template_with_icon},
          'headerTooltip': 'Least Developed Countries',
          },
         {'field': 'AS',
          "headerComponentParams": {"template": header_template_with_icon},
          'headerTooltip': 'African States',
          "cellClass": 'center-flex-cell', "cellRenderer": "CheckBool"}
     ]},
    {'headerName': 'Readiness Programme', "headerClass": 'center-aligned-header', "suppressStickyLabel": True,
     # 'headerTooltip': '''<u>**[Non-annex 1 countries:](https://unfccc.int/parties-observers)**</u>''',

     # https://www.greenclimate.fund/readiness
     # is designed to provide resources for capacity-building activities and technical assistance to enable
     # countries to directly access GCF funds.the programme has supported countries in strengthening their institutional capacities,
     # coordination mechanisms, and strategic frameworks, including Nationally Determined
     # Contributions (NDCs) and National Adaptation Plans (NAPs), to develop climate action agendas.
     'children': [
         {'field': 'RP Financing $', 'headerName': 'Financing',
          'cellStyle': {'textAlign': 'right'}, "valueFormatter": {"function": "d3.format('$.4s')(params.value)"},
          "headerComponentParams": {"template": header_template_with_icon},
          'headerTooltip': financing_header_tooltip
          },
         {'field': '# RP', 'headerName': 'Nb of Projects', "cellClass": 'center-flex-cell',
          "cellRenderer": "CustomButtonCell",
          },
     ]},
    {'headerName': 'Funded Activities', "headerClass": 'center-aligned-header', "suppressStickyLabel": True,
     # https://www.greenclimate.fund/projects/access-funding
     'children': [
         {'field': 'FA Financing $', 'headerName': 'Financing',
          'cellStyle': {'textAlign': 'right'}, "valueFormatter": {"function": "d3.format('$.4s')(params.value)"},
          "headerComponentParams": {"template": header_template_with_icon},
          'headerTooltip': financing_header_tooltip
          },
         {'field': '# FA', 'headerName': 'Nb of Projects', "cellClass": 'center-flex-cell',
          "cellRenderer": "CustomButtonCell", "width": 140
          }
     ]},
]

defaultColDef = {
    "headerClass": 'center-aligned-header',
    'filter': True, "filterParams": {"buttons": ["reset"]}, "floatingFilter": True,
    'suppressHeaderMenuButton': True,
    "tooltipComponent": "CustomTooltipHeaders",
}

dashGridOptions = {
    "headerHeight": 30,
    'tooltipShowDelay': 500,
    'tooltipHideDelay': 15000,
    'tooltipInteraction': True,
    "popupParent": {"function": "setPopupsParent()"}
}

countries_grid = html.Div([
    dag.AgGrid(
        id="countries-grid",
        rowData=df_countries.to_dict("records"),
        columnDefs=columnDefs,
        defaultColDef=defaultColDef,
        dashGridOptions=dashGridOptions,
        dangerously_allow_code=True,
        columnSize="autoSize",
        style={
            "height": '100%',
            "width": 1390,
            'box-shadow': 'var(--mantine-shadow-md)',
        },
    )
], style={"flex": 1, 'display': 'flex', 'justify-content': 'center', 'width': '100%', 'overflow': 'auto'})


@callback(
    Output("countries-grid", "dashGridOptions"),
    Input("countries-grid", "virtualRowData"),
)
def row_pinning_bottom(virtual_data):
    if virtual_data:
        cols = ['RP Financing $', '# RP', 'FA Financing $', '# FA']
        dff = pd.DataFrame(virtual_data, columns=cols)

        totals = dff[cols].sum()

        grid_option_patch = Patch()
        grid_option_patch["pinnedBottomRowData"] = [{"Country Name": "TOTAL", **{col: totals[col] for col in cols}}]
        return grid_option_patch
    return no_update


@callback(
    Output("dashboard-segmented-control", "value", allow_duplicate=True),
    Output("readiness-grid-filter-state-store", "data", allow_duplicate=True),
    Output("fa-grid-filter-state-store", "data", allow_duplicate=True),
    Input("countries-grid", "cellRendererData"),
    prevent_initial_call=True
)
def cell_icon_click(click_data):
    if not click_data:
        return no_update

    if click_data['colId'] == '# RP':
        grid_filter = {'Country': {'filterType': 'text', 'type': 'contains', 'filter': click_data['value']}}
        return "readiness", json.dumps(grid_filter), no_update
    elif click_data['colId'] == '# FA':
        grid_filter = {'Countries': {'filterType': 'text', 'type': 'contains', 'filter': click_data['value']}}
        return "fa", no_update, json.dumps(grid_filter)
    else:
        return no_update


@callback(
    Output("countries-grid-filter-state-store", "data", allow_duplicate=True),
    Input("countries-grid", "filterModel"),
    prevent_initial_call=True
)
def save_filter(filter_model):
    # save the current filter state to reapply it when switching tabs
    return json.dumps(filter_model)


@callback(
    Output("countries-grid", "className"),
    Input("color-scheme-switch", "checked"),
)
def countries_grid_switch_theme(checked):
    return "ag-theme-quartz" if checked else "ag-theme-quartz-dark"
