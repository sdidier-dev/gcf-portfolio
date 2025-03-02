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
          "cellRenderer": "ExternalLinkCell", "filterParams": {"maxNumConditions": 10, "buttons": ["reset"]}},
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
     'cellStyle': {'display': 'flex', 'alignItems': 'center'}, 'width': 300,
     "filterParams": {"maxNumConditions": 200, "buttons": ["reset"]}
     },
    {'field': 'Priority States', 'headerName': 'Priority State(s)', "cellClass": 'center-flex-cell',
     "cellRenderer": "CheckBool", 'width': 100
     },
    {'field': 'Entity', 'tooltipField': 'Entity Name', "filterParams": {"maxNumConditions": 200, "buttons": ["reset"]}},
    {'field': 'BM', 'headerName': 'Board Meeting', "cellClass": 'center-flex-cell', "pinned": "right", 'width': 100,
     "valueFormatter": {"function": "'B.' + params.value"}
     },
    {'field': 'FA Financing', 'headerTooltip': 'Funded Activities Financing', 'cellStyle': {'textAlign': 'right'},
     "valueFormatter": {"function": "formatMoneyNumberSI(params.value)"},
     "pinned": "right", 'width': 100
     },
    # add this col as hidden to use it with filter, clicking on figs
    {'field': 'Multi Country', 'hide': True}
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
                # "maxWidth": 2225,
            },
        )
    ], style={"flex": 1, 'display': 'flex', 'justifyContent': 'center', 'width': '100%', 'maxWidth': 1800,
              'overflow': 'auto', 'boxShadow': 'var(--mantine-shadow-md)'})


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
    'priorityState': {'field': 'Priority States', 'type': 'bool'},
    'entity': {'field': 'Entity', 'type': 'text'},
    'BM': {'field': 'BM', 'type': 'text'},
    'FAfin': {'field': 'FA Financing', 'type': 'num'},
    'multiCountry': {'field': 'Multi Country', 'type': 'bool'},
}
col_to_query['fa'] = {v['field']: k for k, v in query_to_col['fa'].items()}


@callback(
    Output({'type': 'grid', 'index': 'fa'}, "filterModel", allow_duplicate=True),
    Input({'type': 'figure', 'subtype': 'line', 'index': 'fa'}, "clickData"),
    State({'type': 'grid', 'index': 'fa'}, "filterModel"),
    prevent_initial_call=True
)
def fa_timeline_click(click_data, filter_model):
    if not click_data:
        return no_update

    selected_board = click_data['points'][0]['x']
    filter_model['BM'] = {'filterType': 'number', 'type': 'equals', 'filter': selected_board}
    return filter_model


@callback(
    Output({'type': 'grid', 'index': 'fa'}, "filterModel", allow_duplicate=True),
    Input({'type': 'figure', 'subtype': 'bar', 'index': 'fa'}, "clickData"),
    State({'type': 'grid', 'index': 'fa'}, "filterModel"),
    prevent_initial_call=True
)
def fa_cat_bar_click(click_data, filter_model):
    if not click_data:
        return no_update

    selected_col = click_data['points'][0]['y']
    selected_cat = click_data['points'][0]['customdata'][0]

    if selected_col in ['Priority States', 'Multi Country']:  # bool
        filter_model[selected_col] = {'filterType': 'text', 'type': 'true' if selected_cat == 'Yes' else 'false'}
    else:
        filter_model[selected_col] = {'filterType': 'text', 'type': 'contains', 'filter': selected_cat}
    return filter_model


@callback(
    Output({'type': 'grid', 'index': 'fa'}, "filterModel", allow_duplicate=True),
    Input({'type': 'figure', 'subtype': 'histogram', 'index': 'fa'}, "clickData"),
    State({'type': 'grid', 'index': 'fa'}, "filterModel"),
    prevent_initial_call=True
)
def fa_histogram_click(click_data, filter_model):
    if not click_data:
        return no_update
    # need to rework the bins first

    # print(click_data)
    return no_update

    # selected_partner = click_data['points'][0]['y']
    # filter_model['Delivery Partner'] = {'filterType': 'text', 'type': 'contains', 'filter': selected_partner}
    # return filter_model
