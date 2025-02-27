import os

import pandas as pd
from dash import Input, Output, State, callback, no_update, Patch, html
import dash_ag_grid as dag

from dotenv import load_dotenv

from app_config import df_countries, header_template_with_icon, query_to_col, col_to_query

# load env variable to know if the app is local or deployed
load_dotenv()

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
                               ": {'display': 'flex', 'align-items': 'center', 'gap': 10,}"},
     "filterParams": {"maxNumConditions": 200, "buttons": ["reset"]},
     },
    {'field': 'Region', "filterParams": {"maxNumConditions": 5, "buttons": ["reset"]}},
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


def countries_grid(theme='light'):
    return html.Div([
        dag.AgGrid(
            id={'type': 'grid', 'index': 'countries'},
            rowData=df_countries.to_dict("records"),
            columnDefs=columnDefs,
            defaultColDef=defaultColDef,
            dashGridOptions=dashGridOptions,
            dangerously_allow_code=True,
            columnSize="autoSize",
            className=f"ag-theme-quartz{'' if theme == 'light' else '-dark'}",
            style={"height": '100%', "width": 1390, 'box-shadow': 'var(--mantine-shadow-md)'},
        )
    ], style={"flex": 1, 'display': 'flex', 'justify-content': 'center', 'width': '100%', 'overflow': 'auto'})


# mapping field/queries
query_to_col['countries'] = {
    'country': {'field': 'Country Name', 'type': 'text'},
    'region': {'field': 'Region', 'type': 'text'},
    'SIDS': {'field': 'SIDS', 'type': 'bool'},
    'LDC': {'field': 'LDC', 'type': 'bool'},
    'AS': {'field': 'AS', 'type': 'bool'},
    'priorityStates': {'field': 'Priority States', 'type': 'bool'},
    'RPfin': {'field': 'RP Financing $', 'type': 'num'},
    'RPnb': {'field': '# RP', 'type': 'num'},
    'FAfin': {'field': 'FA Financing $', 'type': 'num'},
    'FAnb': {'field': '# FA', 'type': 'num'},
}
col_to_query['countries'] = {v['field']: k for k, v in query_to_col['countries'].items()}


@callback(
    Output({'type': 'grid', 'index': 'countries'}, "dashGridOptions"),
    Input({'type': 'grid', 'index': 'countries'}, "virtualRowData"),
)
def row_pinning_bottom(virtual_data):
    if not virtual_data:
        return no_update

    cols = ['RP Financing $', '# RP', 'FA Financing $', '# FA']
    dff = pd.DataFrame(virtual_data, columns=cols)

    totals = dff[cols].sum()

    grid_option_patch = Patch()
    grid_option_patch["pinnedBottomRowData"] = [{"Country Name": "TOTAL", **{col: totals[col] for col in cols}}]
    return grid_option_patch


@callback(
    Output("url-location", "pathname", allow_duplicate=True),
    Output("url-location", "search", allow_duplicate=True),
    Output("url-location", "refresh", allow_duplicate=True),
    Input({'type': 'grid', 'index': 'countries'}, "cellRendererData"),
    State({'type': 'grid', 'index': 'countries'}, "virtualRowData"),
    prevent_initial_call=True
)
def cell_icon_click(click_data, virtual_data):
    if not click_data:
        return no_update

    # Note: DASH_URL_BASE_PATHNAME needs a trailing '/', so must be removed from the subdomains below
    base_path = os.getenv('DASH_URL_BASE_PATHNAME', '/')

    if click_data['colId'] == '# RP':
        if click_data['value'] == 'TOTAL':
            countries = [row['Country Name'].replace(' ', '_') for row in virtual_data]
            query = f"?{col_to_query['readiness']['Country']}={'+'.join(countries)}"
        else:
            query = f"?{col_to_query['readiness']['Country']}={click_data['value']}"
        return base_path + "readiness", query, 'callback-nav'

    elif click_data['colId'] == '# FA':
        if click_data['value'] == 'TOTAL':
            countries = [row['Country Name'].replace(' ', '_') for row in virtual_data]
            query = f"?{col_to_query['fa']['Countries']}={'+'.join(countries)}"
        else:
            query = f"?{col_to_query['fa']['Countries']}={click_data['value']}"
        return base_path + "funded-activities", query, 'callback-nav'

    else:
        return no_update


@callback(
    Output({'type': 'grid', 'index': 'countries'}, "filterModel", allow_duplicate=True),
    Input({'type': 'figure', 'subtype': 'map', 'index': 'countries'}, "clickData"),
    State("countries-map-carousel-3", "active"),
    prevent_initial_call=True
)
def countries_map_click(click_data, carousel_3):
    if not click_data:
        return no_update

    selected_country = click_data['points'][0]['customdata'][1]

    return {"Region" if carousel_3 else 'Country Name': {
        'filterType': 'text', 'type': 'contains', 'filter': selected_country}}


@callback(
    Output({'type': 'grid', 'index': 'countries'}, "filterModel", allow_duplicate=True),
    Input({'type': 'figure', 'subtype': 'parcats', 'index': 'countries'}, "clickData"),
    State({'type': 'figure', 'subtype': 'parcats', 'index': 'countries'}, "figure"),
    prevent_initial_call=True
)
def countries_parcats_click(click_data, fig):
    if not click_data:
        return no_update
    points = [p['pointNumber'] for p in click_data['points']]

    grid_filter = {}
    for dim in fig['data'][0]['dimensions']:
        # get the categories set of clicked points, if only one cat, it is added for the grid filter
        if len(cat := set(dim['values'][i] for i in points)) == 1:
            if dim['label'] == 'REGION':
                text = cat.pop().replace('<br>', ' ')
                grid_filter['Region'] = {'filterType': 'text', 'type': 'contains', 'filter': text}
            elif dim['label'] == 'PRIORITY STATES':
                grid_filter['Priority States'] = {'filterType': 'text', 'type': 'true' if cat == {'Yes'} else 'false'}
            else:
                grid_filter[dim['label']] = {'filterType': 'text', 'type': 'true' if cat == {'Yes'} else 'false'}
    return grid_filter
