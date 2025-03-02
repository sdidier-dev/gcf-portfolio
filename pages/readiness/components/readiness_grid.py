import json
import os
from pprint import pprint

import pandas as pd
from dash import Dash, _dash_renderer, Input, Output, State, callback, clientside_callback, no_update, Patch, html
import dash_ag_grid as dag

import dash_mantine_components as dmc
from dash_iconify import DashIconify

from app_config import df_readiness, header_template_with_icon, query_to_col, col_to_query

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

ref_col = {'field': 'Ref #', "filterParams": {"maxNumConditions": 10, "buttons": ["reset"]}}
project_col = {'field': 'Project Title', 'tooltipField': 'Project Title',
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
    'cellStyle': {'display': 'flex', 'alignItems': 'center'},
    "filterParams": {"maxNumConditions": 200, "buttons": ["reset"]},
}
region_col = {'field': 'Region', 'width': 150, "filterParams": {"maxNumConditions": 5, "buttons": ["reset"]}}
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
              "cellClass": 'center-flex-cell', "pinned": "right",
              "filterParams": {"maxNumConditions": 5, "buttons": ["reset"]},
              }

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
    'filter': True, "filterParams": {"maxNumConditions": 1, "buttons": ["reset"]}, "floatingFilter": True,
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


def readiness_grid(theme='light'):
    return html.Div([
        dag.AgGrid(
            id={'type': 'grid', 'index': 'readiness'},
            rowData=df_readiness.to_dict("records"),
            columnDefs=columnDefs,
            defaultColDef=defaultColDef,
            dashGridOptions=dashGridOptions,
            dangerously_allow_code=True,
            columnSize="autoSize",
            columnSizeOptions={'keys': [
                'Ref #', 'Delivery Partner', 'Region', 'SIDS', 'LDC', 'NAP', 'Status', 'Approved Date', 'Financing'
            ]},
            className=f"ag-theme-quartz{'' if theme == 'light' else '-dark'}",
            style={"height": '100%', "maxWidth": 2225},
        )
    ], style={"flex": 1, 'display': 'flex', 'justifyContent': 'center', 'width': '100%', 'overflow': 'auto',
              'boxShadow': 'var(--mantine-shadow-md)'})


query_to_col['readiness'] = {
    'ref': {'field': 'Ref #', 'type': 'text'},
    'project': {'field': 'Project Title', 'type': 'text'},
    'activity': {'field': 'Activity', 'type': 'text'},
    'NAP': {'field': 'NAP', 'type': 'bool'},
    'deliveryPartner': {'field': 'Delivery Partner', 'type': 'text'},
    'country': {'field': 'Country', 'type': 'text'},
    'region': {'field': 'Region', 'type': 'text'},
    'SIDS': {'field': 'SIDS', 'type': 'bool'},
    'LDC': {'field': 'LDC', 'type': 'bool'},
    'AS': {'field': 'AS', 'type': 'bool'},
    'status': {'field': 'Status', 'type': 'text'},
    # 'approvedDate': {'field': 'Approved Date str', 'type': 'num'},
    'financing': {'field': 'Financing', 'type': 'num'},
}
col_to_query['readiness'] = {v['field']: k for k, v in query_to_col['readiness'].items()}


@callback(
    Output({'type': 'grid', 'index': 'readiness'}, "filterModel", allow_duplicate=True),
    Input({'type': 'figure', 'subtype': 'bar', 'index': 'readiness-status'}, "clickData"),
    State({'type': 'grid', 'index': 'readiness'}, "filterModel"),
    prevent_initial_call=True
)
def readiness_status_bar_click(click_data, filter_model):
    if not click_data:
        return no_update

    selected_status = click_data['points'][0]['y']
    filter_model['Status'] = {'filterType': 'text', 'type': 'contains', 'filter': selected_status}
    return filter_model


@callback(
    Output({'type': 'grid', 'index': 'readiness'}, "filterModel", allow_duplicate=True),
    Input({'type': 'figure', 'subtype': 'line+bar', 'index': 'readiness-timeline'}, "clickData"),
    Input('readiness-timeline-dropdown', "value"),
    State({'type': 'grid', 'index': 'readiness'}, "filterModel"),
    prevent_initial_call=True
)
def readiness_timeline_click(click_data, agg, filter_model):
    if not click_data:
        return no_update

    # need to deal with the dates in querry firs
    # try to use fig zoom to select a date rage that will be applied to the grid

    # line
    # selected_date = click_data['points'][0]['x']

    # 'curveNumber': 1,
    # selected_end_date = click_data['points'][0]['x']

    # {"value": "M1", "label": "Month"},
    # {"value": "M3", "label": "Quarter"},
    # {"value": "M6", "label": "Half Year"},
    # {"value": "M12", "label": "Year"},
    # {"value": "GCF", "label": "GCF Replenishments"},

    # pprint(click_data)

    # filter_model['Status'] = {'filterType': 'text', 'type': 'contains', 'filter': selected_status}

    return no_update


@callback(
    Output({'type': 'grid', 'index': 'readiness'}, "filterModel", allow_duplicate=True),
    Input({'type': 'figure', 'subtype': 'bar', 'index': 'readiness-top-partners'}, "clickData"),
    State({'type': 'grid', 'index': 'readiness'}, "filterModel"),
    prevent_initial_call=True
)
def readiness_top_partners_bar_click(click_data, filter_model):
    if not click_data:
        return no_update

    selected_partner = click_data['points'][0]['y']
    filter_model['Delivery Partner'] = {'filterType': 'text', 'type': 'contains', 'filter': selected_partner}
    return filter_model
