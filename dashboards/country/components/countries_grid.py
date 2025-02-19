import json
import os

import pandas as pd
from dash import Dash, _dash_renderer, Input, Output, State, callback, clientside_callback, no_update, Patch, html
import dash_ag_grid as dag

import dash_mantine_components as dmc
from dash_iconify import DashIconify

from app_config import df_countries, header_template_with_icon

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
          "cellClass": 'center-flex-cell', "cellRenderer": "CheckBool"},
         # add this col as hidden to use it with filter, clicking on the parcats fig
         {'field': 'Priority States', 'hide': True}
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
          'cellStyle': {'textAlign': 'right'},
          "valueFormatter": {"function": "formatMoneyNumberSI(params.value)"},
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
          'cellStyle': {'textAlign': 'right'},
          "valueFormatter": {"function": "formatMoneyNumberSI(params.value)"},
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
    Output("countries-grid", "filterModel"),
    Input("countries-grid", "id"),
    State("countries-grid-filter-state-store", "data"),
)
def apply_filter(_, temp_filter):
    # apply existing filter from the store once the grid is ready,
    return json.loads(temp_filter) if temp_filter else no_update


@callback(
    Output("countries-grid-filter-state-store", "data", allow_duplicate=True),
    Input("countries-grid", "filterModel"),
    prevent_initial_call=True
)
def save_filter(filter_model):
    # save the current filter state to reapply it when switching tabs
    return json.dumps(filter_model) if filter_model else no_update


@callback(
    Output("countries-grid", "filterModel", allow_duplicate=True),
    Input("countries-grid-reset-btn", "n_clicks"),
    prevent_initial_call=True
)
def reset_filter(_):
    return {}


@callback(
    Output("countries-grid", "className"),
    Input("color-scheme-switch", "checked"),
)
def countries_grid_switch_theme(checked):
    return "ag-theme-quartz" if checked else "ag-theme-quartz-dark"
