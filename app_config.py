import os
from datetime import datetime

import numpy as np
import pandas as pd

assets_folder = os.path.join(os.path.abspath(os.curdir), 'assets')

df_countries = pd.read_csv(f'{assets_folder}/GCF-countries.csv')
df_readiness = pd.read_csv(
    f'{assets_folder}/GCF-readiness.csv', date_format={'Approved Date': '%b %d, %Y'}, parse_dates=['Approved Date']
)
df_entities = pd.read_csv(f'{assets_folder}/GCF-entities.csv')

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

# ['ISO3', 'Country Name', 'Region', 'SIDS', 'LDC', '# RP', '# FA',
# 'RP Financing $', 'FA Financing $', 'AS', 'priority state',
# '# RP region_sum', '# FA region_sum', 'RP Financing $ region_sum', 'FA Financing $ region_sum']

# Readiness Data #####################################################################################
# ISO string format date, note that it will text type at this point to be able to parse it with dag
df_readiness['Approved Date'] = df_readiness['Approved Date'].dt.strftime('%Y-%m-%d')

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

# add the name of the entities from the 'entities' dataframe
df_readiness = pd.merge(
    df_readiness, df_entities[['Entity', 'Name']],
    left_on='Delivery Partner', right_on='Entity', how='left'
)
df_readiness.drop('Entity', axis=1, inplace=True)
df_readiness.rename(columns={"Name": "Partner Name"}, inplace=True)

# ['Ref #', 'Activity', 'Project Title', 'Country', 'Delivery Partner',
# 'Region', 'SIDS', 'LDCs', 'NAP', 'Status', 'Approved Date', 'Financing', 'AS', "Partner Name"]

# Funded Activities Data #####################################################################################

# Entities Data #####################################################################################
