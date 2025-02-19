import os
from datetime import datetime

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
