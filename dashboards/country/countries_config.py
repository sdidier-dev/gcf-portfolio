import os

import numpy as np
import pandas as pd

assets_folder = os.path.join(os.path.abspath(os.curdir), 'assets')

df_GCF_countries = pd.read_csv(f'{assets_folder}/GCF-countries.csv')
df_GCF_countries.rename(columns={"LDCs": "LDC"}, inplace=True)
df_GCF_countries.fillna(value=0, inplace=True)
df_GCF_countries['AS'] = df_GCF_countries['Region'] == 'Africa'
# df_GCF_countries.columns

# add cols for sum by region
region_sum = df_GCF_countries.groupby('Region')[['# RP', '# FA', 'RP Financing $', 'FA Financing $']].sum()
df_GCF_countries = df_GCF_countries.assign(**{
    f'{col} region_sum': df_GCF_countries['Region'].apply(lambda row: region_sum[col][row])
    for col in ['# RP', '# FA', 'RP Financing $', 'FA Financing $']
})

# add 'priority states' col
df_GCF_countries['priority state'] = df_GCF_countries[['SIDS', 'LDC', 'AS']].any(axis=1)
