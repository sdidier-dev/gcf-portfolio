import os
from datetime import datetime

import numpy as np
import pandas as pd

from dashboards.entities.entities_dashboard import entities_dashboard

# Main constants #####################################################################################
PRIMARY_COLOR = '#15a14a'
SECONDARY_COLOR = '#084081'

# Load datasets #####################################################################################

assets_folder = os.path.join(os.path.abspath(os.curdir), 'assets')

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
df_countries['priority state'] = df_countries[['SIDS', 'LDC', 'AS']].any(axis=1)

# Entities Data #####################################################################################
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
# fill missing entity Name with '*Details Missing*'
df_FA['Entity Name'] = df_FA['Entity Name'].fillna('*Details Missing*')
