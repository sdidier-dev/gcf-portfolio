import os
from pprint import pprint
from datetime import timedelta, datetime

import numpy as np
from dash import dcc, html, Input, Output, State, callback, no_update, clientside_callback, Patch, ctx
import dash_mantine_components as dmc
import plotly.graph_objects as go
import plotly.io as pio
import plotly.express as px
from plotly.subplots import make_subplots

import pandas as pd

from app_config import df_FA, format_money_number_si, SECONDARY_COLOR

cat_cols = {
    'Theme': {'Adaptation': '#15a14a', 'Cross-cutting': '#158575', 'Mitigation': '#1569a1'},
    'Sector': {'Private': '#15a14a', 'Public': '#1569a1'},
    'Project Size': {'Large': '#15a14a', 'Medium': '#158575', 'Small': '#3498db',
                     'Micro': '#1569a1', '*Missing*': '#9b59b6'},
    'ESS Category': {'Category C': '#15a14a', 'Category B': '#27ae60', 'Category A': '#2ecc71',
                     'Intermediation 3': '#1569a1', 'Intermediation 2': '#2980b9', 'Intermediation 1': '#3498db'},
    'Priority State': {'Yes': '#15a14a', 'No': '#1569a1'},
    'Multiple Countries': {'No': '#15a14a', 'Yes': '#1569a1'},
    'Modality': {'PAP': '#15a14a', 'SAP': '#1569a1'},
}

total_color = '#d4ac0d'
total_financing_sum = df_FA['FA Financing'].sum()


def cat_hover(col, cat):
    if col == 'Priority State':
        return 'Priority States' if cat == 'Yes' else 'Not Priority States'
    elif col == 'Multiple Countries':
        return 'Multiple Countries Projects' if cat == 'Yes' else 'Single Country Projects'
    elif col == 'Modality':
        return 'Proposal Approval Process (standard)' if cat == 'PAP' else 'Simplified Approval Process'
    else:
        return f"{col}: {cat}"


fig = go.Figure()
for col in cat_cols:
    dff = pd.DataFrame(df_FA.groupby(col)['FA Financing'].sum())
    dff['Number'] = df_FA[col].value_counts()

    # rename bool as Yes/No
    if col in ['Priority State', 'Multiple Countries']:
        dff = dff.rename({True: 'Yes', False: 'No'})

    for cat in cat_cols[col]:
        fig.add_bar(
            orientation='h',
            name=cat,
            x=[dff['FA Financing'][cat]],
            y=[col],
            textfont={'color': 'var(--mantine-color-text)'},
            textposition="inside", insidetextanchor="middle", textangle=0,
            # customdata: 0=cat, 1=financing %, 2=number, 3=cat_hover
            customdata=[(cat, dff['FA Financing'][cat] / total_financing_sum, dff['Number'][cat], cat_hover(col, cat))],
            texttemplate="<b>%{customdata[0]} %{customdata[1]:.0%}</b><br>"
                         "%{x:$.4s} (%{customdata[2]})<br>",
            hovertemplate="<b>%{customdata[3]}</b><br>"
                          "%{customdata[1]:.0%} of Total<br>"
                          "%{x:$.4s} (%{customdata[2]})<extra></extra>",
            marker=dict(
                color=cat_cols[col][cat],
                line={'color': cat_cols[col][cat], 'width': 2},
                # Trick to add transparency to the color marker only, not the border, as marker_opacity applies to both
                pattern={'fillmode': "replace", 'shape': "/", 'solidity': 1,
                         'fgcolor': cat_cols[col][cat], 'fgopacity': 0.5}
            ),
        )

# add zero and total lines
fig.add_vline(x=0, line={'color': 'var(--mantine-color-text)', 'width': 5})
fig.add_vline(x=total_financing_sum, line={'color': total_color, 'width': 5})
fig.add_annotation(
    showarrow=False,
    x=total_financing_sum,
    yref="y domain", yanchor="bottom", y=1,
    font={'size': 16, 'color': total_color, 'weight': "bold"},
    text='$' + format_money_number_si(total_financing_sum),
)

fig.update_xaxes(
    title={'text': 'Financing', 'font_size': 16, 'font_weight': "bold"},
    range=[0, total_financing_sum * 1.03],
    showgrid=False, showline=True, linewidth=2,
    ticks="outside", tickwidth=2, tickprefix='$'
)
fig.update_yaxes(tickfont_weight="bold", autorange="reversed")

fig.update_layout(
    barmode='stack',
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin={"r": 20, "t": 20, "l": 0, "b": 0},
    showlegend=False,
)
FA_bar = dcc.Graph(
    id='fa-bar-graph',
    config={'displayModeBar': False}, responsive=True,
    figure=fig,
    style={"flex": 1, "padding": 10},
)


@callback(
    Output("fa-bar-graph", "figure", allow_duplicate=True),
    Input("fa-bar-carousel", "active"),
    Input("fa-grid", "virtualRowData"),
    State("fa-bar-graph", "figure"),
    prevent_initial_call=True
)
def update_fa_timeline_data(carousel, virtual_data, fig):
    patched_fig = Patch()
    if not virtual_data:
        for i, trace in enumerate(fig['data']):
            patched_fig["data"][i]['x'] = None
            patched_fig["layout"]['shapes'][1]['x0'] = 0
            patched_fig["layout"]['shapes'][1]['x1'] = 0
            patched_fig["layout"]['annotations'][0]['x'] = 0
            patched_fig["layout"]['annotations'][0]['text'] = 0
            patched_fig["layout"]['xaxis']['range'] = None
        return patched_fig

    dff_grid = pd.DataFrame(virtual_data)

    total_financing_sum = dff_grid['FA Financing'].sum()
    total_number_sum = len(dff_grid)

    # precompute dff for each col to not calculate the same dff for each cat of the same col
    dff_cols = {}
    for col in cat_cols:
        dff_cols[col] = pd.DataFrame(dff_grid.groupby(col)['FA Financing'].sum())
        dff_cols[col]['Number'] = dff_grid[col].value_counts()
        if col in ['Priority State', 'Multiple Countries']:
            dff_cols[col] = dff_cols[col].rename({True: 'Yes', False: 'No'})

    for i, trace in enumerate(fig['data']):
        col = trace['y'][0]
        cat = trace['name']

        dff = dff_cols[col]

        if cat not in dff.index:
            # set x=0 for the cat will hide the bar so no need to update customdata, texttemplate, hovertemplate
            patched_fig["data"][i]['x'] = [0]
        else:
            # carousel 0=Financing, 1=Number
            if carousel:
                x = [dff['Number'][cat]]
                # customdata: 0=cat, 1=number %, 2=financing, 3=cat_hover
                customdata = [(cat, dff['Number'][cat] / total_number_sum,
                               dff['FA Financing'][cat], cat_hover(col, cat))]
                texttemplate = ("<b>%{customdata[0]} %{customdata[1]:.0%}</b><br>"
                                "%{x} (%{customdata[2]:$.4s})<br>")
                hovertemplate = ("<b>%{customdata[3]}</b><br>"
                                 "%{customdata[1]:.0%} of Total<br>"
                                 "%{x} (%{customdata[2]:$.4s})<extra></extra>")
            else:
                x = [dff['FA Financing'][cat]]
                # customdata: 0=cat, 1=financing %, 2=number, 3=cat_hover
                customdata = [(cat, dff['FA Financing'][cat] / total_financing_sum,
                               dff['Number'][cat], cat_hover(col, cat))]
                texttemplate = ("<b>%{customdata[0]} %{customdata[1]:.0%}</b><br>"
                                "%{x:$.4s} (%{customdata[2]})<br>")
                hovertemplate = ("<b>%{customdata[3]}</b><br>"
                                 "%{customdata[1]:.0%} of Total<br>"
                                 "%{x:$.4s} (%{customdata[2]})<extra></extra>")

            patched_fig["data"][i]['x'] = x
            patched_fig["data"][i]['customdata'] = customdata
            patched_fig["data"][i]['texttemplate'] = texttemplate
            patched_fig["data"][i]['hovertemplate'] = hovertemplate

    # update total line and annotation
    patched_fig["layout"]['shapes'][1]['x0'] = total_number_sum if carousel else total_financing_sum
    patched_fig["layout"]['shapes'][1]['x1'] = total_number_sum if carousel else total_financing_sum
    patched_fig["layout"]['annotations'][0]['x'] = total_number_sum if carousel else total_financing_sum
    text = total_number_sum if carousel else '$' + format_money_number_si(total_financing_sum)
    patched_fig["layout"]['annotations'][0]['text'] = text
    # update x axis
    patched_fig["layout"]['xaxis']['title']['text'] = 'Number of Projects' if carousel else 'Financing'
    patched_fig["layout"]['xaxis']['range'] = [0, (total_number_sum if carousel else total_financing_sum) * 1.03]
    patched_fig["layout"]['xaxis']['tickprefix'] = '' if carousel else '$'

    return patched_fig


@callback(
    Output("fa-bar-graph", "figure"),
    Input("color-scheme-switch", "checked"),
)
def update_figure_theme(checked):
    patched_fig = Patch()
    patched_fig["layout"]["template"] = pio.templates[f"mantine_{'light' if checked else 'dark'}"]
    return patched_fig
