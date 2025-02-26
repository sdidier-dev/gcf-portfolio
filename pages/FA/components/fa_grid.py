import json
import os

import pandas as pd
from dash import Dash, _dash_renderer, Input, Output, State, callback, clientside_callback, no_update, Patch, html
import dash_ag_grid as dag

import dash_mantine_components as dmc
from dash_iconify import DashIconify

from app_config import df_FA, header_template_with_icon, query_to_col, col_to_query

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
    {'headerName': 'Project', "headerClass": 'center-aligned-header', "suppressStickyLabel": True,
     'children': [
         {'field': 'Ref #', 'headerName': 'Reference', "cellClass": 'center-flex-cell', 'width': 100,
          "filterParams": {"maxNumConditions": 10, "buttons": ["reset"]}},
         {'field': 'Modality', "cellClass": 'center-flex-cell', 'width': 100},
         {'field': 'Project Name', 'tooltipField': 'Project Name', 'width': 300},
         {'field': 'Theme', "cellClass": 'center-flex-cell', 'width': 130},
         {'field': 'Sector', "cellClass": 'center-flex-cell', 'width': 130},
         {'field': 'Project Size', "cellClass": 'center-flex-cell', 'width': 130,
          "filterParams": {"maxNumConditions": 5, "buttons": ["reset"]}},
         {'field': 'ESS Category', 'headerTooltip': 'Environmental and Social Safeguards Category', 'width': 150,
          "filterParams": {"maxNumConditions": 5, "buttons": ["reset"]}},
     ]
     },
    {'field': 'Countries',
     "cellRenderer": "CountriesCell",
     'tooltipField': 'Countries', "tooltipComponent": "CustomTooltipCountries",
     'cellStyle': {'display': 'flex', 'align-items': 'center'}, 'width': 300,
     "filterParams": {"maxNumConditions": 200, "buttons": ["reset"]}
     },
    {'field': 'Priority State', 'headerName': 'Priority State(s)', "cellClass": 'center-flex-cell',
     "cellRenderer": "CheckBool", 'width': 100
     },
    {'field': 'Entity', 'tooltipField': 'Entity Name', "filterParams": {"maxNumConditions": 5, "buttons": ["reset"]}},
    {'field': 'BM', 'headerName': 'Board Meeting', "cellClass": 'center-flex-cell', "pinned": "right", 'width': 100,
     "valueFormatter": {"function": "'B.' + params.value"}
     },
    {'field': 'FA Financing', 'headerTooltip': 'Funded Activities Financing', 'cellStyle': {'textAlign': 'right'},
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


def fa_grid(theme='light'):
    return html.Div([
        dag.AgGrid(
            id={'type': 'grid', 'index': 'fa'},
            rowData=df_FA.to_dict("records"),
            columnDefs=columnDefs,
            defaultColDef=defaultColDef,
            dashGridOptions=dashGridOptions,
            dangerously_allow_code=True,
            className=f"ag-theme-quartz{'' if theme == 'light' else '-dark'}",
            style={
                "height": '100%',
                # "max-width": 2225,
                'box-shadow': 'var(--mantine-shadow-md)',
            },
        )
    ], style={"flex": 1, 'display': 'flex', 'justify-content': 'center', 'width': '100%', 'maxWidth': 1800,
              'overflow': 'auto'})


# mapping field/queries
query_to_col['fa'] = {
    'ref': {'field': 'Ref #', 'type': 'text'},
    'modality': {'field': 'Modality', 'type': 'text'},
    'project': {'field': 'Project Name', 'type': 'text'},
    'theme': {'field': 'Theme', 'type': 'text'},
    'sector': {'field': 'Sector', 'type': 'text'},
    'projectSize': {'field': 'Project Size', 'type': 'text'},
    'ESSCat': {'field': 'ESS Category', 'type': 'text'},
    'countries': {'field': 'Countries', 'type': 'text'},
    'priorityState': {'field': 'Priority State', 'type': 'bool'},
    'entity': {'field': 'Entity', 'type': 'text'},
    'BM': {'field': 'BM', 'type': 'text'},
    'FAfin': {'field': 'FA Financing', 'type': 'num'},
}
col_to_query['fa'] = {v['field']: k for k, v in query_to_col['fa'].items()}
