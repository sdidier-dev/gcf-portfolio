import os
from datetime import datetime

import numpy as np
import pandas as pd

assets_folder = os.path.join(os.path.abspath(os.curdir), 'assets')

df_GCF_readiness = pd.read_csv(
    f'{assets_folder}/GCF-readiness.csv', date_format={'Approved Date': '%b %d, %Y'}, parse_dates=['Approved Date']
)
# ISO string format date, note that it will be as text at this point to be able to parse it with dag
df_GCF_readiness['Approved Date'] = df_GCF_readiness['Approved Date'].dt.strftime('%Y-%m-%d')

# df['Approved Date'] = pd.to_datetime(df['Approved Date'])
# df['Year'] = df['Approved Date'].dt.year

df_GCF_readiness.rename(columns={"LDCs": "LDC"}, inplace=True)
df_GCF_readiness['Region'] = (
    df_GCF_readiness['Region'].str
    .replace('AF', 'Africa')
    .replace('AP', 'Asia-Pacific')
    .replace('EE', 'Eastern Europe')
    .replace('LAC', 'Latin America and the Caribbean')
    .replace('WE', 'Western Europe and Others')
)
df_GCF_readiness['AS'] = df_GCF_readiness['Region'] == 'Africa'

# ['Ref #', 'Activity', 'Project Title', 'Country', 'Delivery Partner',
#        'Region', 'SIDS', 'LDCs', 'NAP', 'Status', 'Approved Date',
#        'Financing']