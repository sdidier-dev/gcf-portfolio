import os
from datetime import datetime
from urllib.parse import parse_qs

import numpy as np
import pandas as pd
import dash_mantine_components as dmc

# Main constants #####################################################################################
PRIMARY_COLOR = '#15a14a'
SECONDARY_COLOR = '#084081'

# Main constants/functions #####################################################################################
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


def text_carousel(text_list: list[str], carousel_id: str):
    return dmc.Carousel(
        [dmc.CarouselSlide(dmc.Center(text, h='100%', fw='bold', td='underline', c='var(--primary)')) for text in
         text_list],
        id=carousel_id,
        orientation="vertical",
        height=40,
        # remove the padding, so the controls are at the max top/bottom of the Carousel
        controlsOffset=-50,
        controlSize=15,
        # custom class to Hide inactive controls and Show controls on hover
        classNames={"control": "carousel-control", "controls": "carousel-controls", "root": "carousel-root"},
        style={'display': 'flex', 'align-items': 'center', 'height': 60}
    )


def format_money_number_si(number):
    units = ['', 'k', 'M', 'B']
    magnitude = 0
    while abs(number) >= 1000 and magnitude < len(units) - 1:
        number /= 1000.0
        magnitude += 1
    return f"${number:.1f}{units[magnitude]}"


# Load datasets #####################################################################################

assets_folder = os.path.join(os.path.abspath(os.curdir), 'assets')

df_countries_ISO_codes = pd.read_csv(f'{assets_folder}/countries_codes_and_coordinates.csv')
df_countries = pd.read_csv(f'{assets_folder}/GCF-countries.csv')
df_entities = pd.read_csv(f'{assets_folder}/GCF-entities.csv')
df_readiness = pd.read_csv(
    f'{assets_folder}/GCF-readiness.csv', date_format={'Approved Date': '%b %d, %Y'}, parse_dates=['Approved Date']
)
df_FA = pd.read_csv(f'{assets_folder}/GCF-FA.csv')

# Country Data #####################################################################################
df_countries.rename(columns={"LDCs": "LDC"}, inplace=True)
df_countries.fillna(value=0, inplace=True)
df_countries['AS'] = df_countries['Region'] == 'Africa'

# add cols for sum by region
region_sum = df_countries.groupby('Region')[['# RP', '# FA', 'RP Financing $', 'FA Financing $']].sum()
df_countries = df_countries.assign(**{
    f'{col} region_sum': df_countries['Region'].apply(lambda row: region_sum[col][row])
    for col in ['# RP', '# FA', 'RP Financing $', 'FA Financing $']
})

# add 'priority states' col
df_countries['Priority States'] = df_countries[['SIDS', 'LDC', 'AS']].any(axis=1)

# Entities Data #####################################################################################
# fix bad data
df_entities['BM'] = df_entities['BM'].fillna('0')
df_entities['Size'] = df_entities['Size'].str.replace('Medium, Small', 'Medium')
# convert the BM col as int to be easier to handle
df_entities['BM'] = df_entities['BM'].str.replace('B.', '', regex=False).astype(int)
# add ISO3 code
df_entities = pd.merge(
    df_entities, df_countries_ISO_codes[['Country', 'Alpha-3 code']], on='Country', how='left')

# extract entities info that will be used for readiness and FA
entities_details = df_entities.drop(columns=['Stage', 'BM', '# Approved', 'FA Financing'])
entities_details.rename(columns={"Name": "Entity Name", "Country": "Entity Country"}, inplace=True)

# Readiness Data #####################################################################################

df_readiness.rename(columns={"LDCs": "LDC"}, inplace=True)
df_readiness['Region'] = (
    df_readiness['Region'].str
    .replace('AF', 'Africa')
    .replace('AP', 'Asia-Pacific')
    .replace('EE', 'Eastern Europe')
    .replace('LAC', 'Latin America and the Caribbean')
    .replace('WE', 'Western Europe and Others')
)
df_readiness['AS'] = df_readiness['Region'] == 'Africa'

# Add a col to have dates in ISO string to parse it with dag
df_readiness['Approved Date str'] = df_readiness['Approved Date'].dt.strftime('%Y-%m-%d')
# add partner info
df_readiness = pd.merge(
    df_readiness, entities_details,
    left_on='Delivery Partner', right_on='Entity', how='left')
df_readiness.drop('Entity', axis=1, inplace=True)
df_readiness.rename(columns={"Entity Country": "Partner Country", "Entity Name": "Partner Name"}, inplace=True)
# fill missing Partner Name with '*Details Missing*' that will be used on hover
df_readiness['Partner Name'] = df_readiness['Partner Name'].fillna('*Details Missing*')

# Funded Activities Data #####################################################################################

# add entity name for hover
df_FA = pd.merge(df_FA, entities_details[['Entity', "Entity Name"]], on='Entity', how='left')
# fill missing data with '*Details Missing*'
df_FA['Entity Name'] = df_FA['Entity Name'].fillna('*Details Missing*')
df_FA['Project Size'] = df_FA['Project Size'].fillna('*Missing*')
# convert the BM col as int to be easier to handle
df_FA['BM'] = df_FA['BM'].str.replace('B.', '', regex=False).astype(int)
# add priority states
priority_countries = df_countries[df_countries['Priority States']]['Country Name'].tolist()
df_FA['Priority States'] = df_FA['Countries'].apply(
    lambda countries: any(country.strip() in priority_countries for country in countries.split(','))
)
# add multi countries
df_FA['Multiple Countries'] = df_FA['Countries'].apply(lambda countries: len(countries.split(',')) > 1)


# URL queries to grid filters and the opposite #################################################################

# parse str to int/float
def parse_as_number(value):
    try:
        return int(value)  # Try parsing as an integer
    except ValueError:
        try:
            return float(value)  # Try parsing as a float
        except ValueError:
            return None  # Not a valid number


# def app wide variables that will be populated in Grids scrips
# those variables are used to map query params names to col names
query_to_col = {}
col_to_query = {}


def query_to_filter(query, query_to_col):
    if not query:
        return {}

    # http://127.0.0.1:8050/countries?country=a+b&country=c&countryOperator=AND&SIDS=true&RPnb=10-20
    filterModel = {}

    query_params = parse_qs(query[1:])  # remove the '?'

    for param, values in query_params.items():
        # first check if the param has a corresponding col else skipped
        if param in query_to_col:

            #  queries examples: ?country=bra, ?country=a+b&country=c&countryOperator=AND, ?country=a_d
            # note the '_' is used to keep the space in the filter instead of splitting the text in 2 filters
            if query_to_col[param]['type'] == 'text':
                # check if operator is provided and its value is valid else operator default to OR
                # note that it will be skipped if only one value in param
                if param + 'Operator' in query_params and query_params[param + 'Operator'][0] in ['AND', 'OR']:
                    operator = query_params[param + 'Operator'][0]
                else:
                    operator = 'OR'

                # split if value is like 'a+b' or 'a b' (note that '+' is parsed as space using parse_qs()
                values = [v.replace('_', ' ') for value in values for v in value.split()]
                filterModel[query_to_col[param]['field']] = {
                    'filterType': 'text', 'operator': operator,
                    'conditions': [{'filterType': 'text', 'type': 'contains', 'filter': value} for value in values]
                }

            # queries examples: ?SIDS=true, ?SIDS=True, ?SIDS=TRUE
            elif query_to_col[param]['type'] == 'bool':
                value = values[0].lower()
                if value in ['true', 'false']:
                    filterModel[query_to_col[param]['field']] = {'filterType': 'text', 'type': value}

            # queries examples: ?RPnb=10, ?RPnb=10-20, ?RPnb=10&RPnbOperator=greaterThan
            elif query_to_col[param]['type'] == 'num':
                # try to split in case of range
                values = values[0].split('-')
                if len(values) == 1:
                    value = parse_as_number(values[0])
                    # process only if value is a number else skip
                    if value is not None:
                        # check if operator is provided and its value is valid else operator default to 'equals'
                        operators = ['greaterThan', 'lessThan', 'equals', 'notEqual',
                                     'greaterThanOrEqual', 'lessThanOrEqual', 'blank', 'notBlank']
                        if param + 'Operator' in query_params and query_params[param + 'Operator'][0] in operators:
                            operator = query_params[param + 'Operator'][0]
                        else:
                            operator = 'equals'

                        filterModel[query_to_col[param]['field']] = {
                            'filterType': 'number', 'type': operator, 'filter': value}
                # range like ?RPnb=10-20
                elif len(values) == 2:
                    values = [parse_as_number(values[0]), parse_as_number(values[1])]
                    # process only if values are both a number else skip
                    if values[0] is not None and values[1] is not None:
                        filterModel[query_to_col[param]['field']] = {
                            'filterType': 'number', 'type': 'inRange', 'filter': values[0], 'filterTo': values[1]}

    return filterModel


def filter_to_query(filter_model, col_to_query):
    if not filter_model:
        return ''

    queries_list = []
    for col, col_filter in filter_model.items():

        if col_filter['filterType'] == 'text':
            if 'conditions' in col_filter:  # multi conditions
                query_value = f"{col_to_query[col]}={'+'.join([cond['filter'] for cond in col_filter['conditions']])}"
                query_operator = f"{col_to_query[col]}Operator={col_filter['operator']}"
                queries_list += [query_value, query_operator]
            else:  # simple condition
                if col_filter['type'] in ['true', 'false']:  # bool
                    queries_list += [f"{col_to_query[col]}={col_filter['type']}"]
                else:  # text
                    queries_list += [f"{col_to_query[col]}={col_filter['filter']}"]

        elif col_filter['filterType'] == 'number':
            if col_filter['type'] == 'inRange':  # range has 'filter' and 'filterTo'
                queries_list += [f"{col_to_query[col]}={col_filter['filter']}-{col_filter['filterTo']}"]
            else:
                queries_list += [f"{col_to_query[col]}={col_filter['filter']}"]
                # no need to add operator when 'equals' as it is the default, that makes the query a bit simpler
                if col_filter['type'] != 'equals':
                    queries_list += [f"{col_to_query[col]}Operator={col_filter['type']}"]
    return '?' + '&'.join(queries_list).replace(' ', '_')
