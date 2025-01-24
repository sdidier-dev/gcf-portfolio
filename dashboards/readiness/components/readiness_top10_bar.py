import os
from pprint import pprint

from dash import dcc, html, Input, Output, State, callback, no_update, clientside_callback, Patch, ctx
import dash_mantine_components as dmc
import plotly.graph_objects as go
import plotly.io as pio

import pandas as pd

from app_config import df_readiness

# Group by 'Delivery Partner' and get both the sum of 'Financing' and the size of each group
top_partners = df_readiness.groupby('Delivery Partner').agg({'Financing': 'sum', 'Delivery Partner': 'size'})
top_partners = top_partners.rename(columns={'Delivery Partner': 'Group Size'})
top_partners = top_partners.sort_values('Financing', ascending=False).head(10)

# add partner full names
partner_names = df_readiness[['Delivery Partner', 'Partner Name']].drop_duplicates()
partner_names = partner_names.set_index('Delivery Partner')
top_partners = pd.merge(
    top_partners, partner_names['Partner Name'],
    left_index=True, right_on='Delivery Partner', how='left'
)

# ['Financing', 'Group Size', 'Partner Name']

fig = go.Figure()
fig.add_bar(
    orientation='h',
    x=top_partners['Financing'],
    y=top_partners.index,
    # customdata=list(zip(
    #     top_projects['Project Title'],
    #     top_projects['NAP'],
    #     top_projects['Country'],
    #     top_projects['Delivery Partner'],
    # )),
    # hovertemplate='%{customdata[1]}, %{customdata[0]}'

    # text=top_projects['Status'],
    # textfont={'color': '#15a14a', 'weight': "bold"},
    texttemplate='%{y} (%{x:$.4s})',
    # hovertemplate="<b>%{y}</b><br>%{x:$.4s} (%{customdata} Projects)<extra></extra>",
)

fig.update_layout(
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    margin={"r": 0, "t": 0, "l": 0, "b": 50},
    showlegend=False,
)
fig.update_xaxes(title={'text': 'Financing', 'standoff': 10, 'font_size': 16, 'font_weight': "bold"},
                 showgrid=False, showline=True, linewidth=2, ticks="inside", tickprefix='$')
fig.update_yaxes(showticklabels=False, autorange="reversed")

readiness_top10_bar = dmc.Stack([
    dmc.Checkbox(id="readiness-top10-chk", label="Stacked", fz=16),
    dcc.Graph(
        id='readiness-top10-bar',
        config={'displayModeBar': False},
        responsive=True,
        figure=fig,
        style={"flex": 1}
    )
], p=10, style={"flex": 1})


@callback(
    Output("readiness-top10-bar", "figure"),
    Input("color-scheme-switch", "checked"),
)
def update_figure_theme(checked):
    patched_fig = Patch()
    patched_fig["layout"]["template"] = pio.templates[f"mantine_{'light' if checked else 'dark'}"]
    return patched_fig
