import os
from pprint import pprint
from datetime import timedelta, datetime

import numpy as np
from dash import dcc, html, Input, Output, State, callback, no_update, clientside_callback, Patch, ctx
import dash_mantine_components as dmc
import plotly.graph_objects as go
import plotly.io as pio
import plotly.express as px

import pandas as pd

from app_config import df_FA, PRIMARY_COLOR, SECONDARY_COLOR

# the keys will be used for the carousel, the values will be used for the traces order and color
cat_cols = {
    'Theme': {'Adaptation': '#15a14a', 'Cross-cutting': '#158575', 'Mitigation': '#1569a1'},
    'Sector': {'Private': '#15a14a', 'Public': '#1569a1'},
    'Project Size': {'Large': '#15a14a', 'Medium': '#158575', 'Small': '#3498db',
                     'Micro': '#1569a1', '*Missing*': '#9b59b6'},
    'ESS Category': {'Category C': '#15a14a', 'Category B': '#27ae60', 'Category A': '#2ecc71',
                     'Intermediation 3': '#1569a1', 'Intermediation 2': '#2980b9', 'Intermediation 1': '#3498db'},
    'Priority State': {'Priority States': '#15a14a', 'Not Priority States': '#1569a1'},
    'Multiple Countries': {'Single Country Projects': '#15a14a', 'Multiple Countries Projects': '#1569a1'},
    'Modality': {'PAP': '#15a14a', 'SAP': '#1569a1'},
}
total_color = '#d4ac0d'

col_init = 'Theme'

# get the sum financing and nb of project by board meeting and selected col
dff = df_FA.groupby([col_init, 'BM'])['FA Financing'].sum().reset_index()
group_sizes = df_FA.groupby([col_init, 'BM']).size().reset_index(name='Number')
dff = pd.merge(dff, group_sizes, on=[col_init, 'BM'])
# get the full range of board meetings
boards = pd.Series(range(dff['BM'].min(), dff['BM'].max() + 1), name='BM')

fig = go.Figure()

for cat in cat_cols[col_init]:
    # merge with Board series to add the missing boards for that cat, add 0 for missing board and
    # sort by BM to be sure there are ordered for the cumulated sum
    df_cat = pd.merge(boards, dff[dff[col_init] == cat], on='BM', how='left').fillna(value=0).sort_values('BM')
    df_cat['cum-sum'] = df_cat['FA Financing'].cumsum()

    fig.add_scatter(
        name=cat,
        mode='lines+markers+text',
        x=df_cat['BM'],
        y=df_cat['cum-sum'],
        line={'color': cat_cols[col_init][cat], 'width': 3},
        marker={'size': 10, 'opacity': [0] * (len(df_cat) - 1) + [1]},
        text=[''] * (len(df_cat) - 1) + [df_cat['cum-sum'].iloc[-1]],
        textposition="middle right", texttemplate="%{text:$.4s}",
        textfont={'size': 14, 'color': cat_cols[col_init][cat], 'weight': "bold"},
        customdata=df_cat['FA Financing'],
        hovertemplate='<b>%{y:$.4s}</b><br>(+%{customdata:$.4s})',
    )

fig.update_xaxes(
    title={'text': 'Board Meeting Number', 'font_size': 16, 'font_weight': "bold"},
    showgrid=False,
    tickprefix='B.',
    dtick=1,
    range=[boards.min(), boards.max()]
)
fig.update_yaxes(
    title={'text': 'Financing', 'font_size': 16, 'font_weight': "bold"},
    tickprefix='$',
    showgrid=False,
    rangemode="tozero"
)
fig.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin={"r": 60, "t": 10, "l": 0, "b": 0},
    legend=dict(xanchor="left", x=0.05, yanchor="top", y=0.95),
    hovermode="x"
)

FA_timeline = dmc.Stack([
    dmc.Group([
        dmc.Checkbox(id="fa-timeline-total-chk", label="Add Total Line"),
        dmc.Checkbox(id="fa-timeline-stack-chk", label="Stack Lines"),
    ]),
    dcc.Graph(
        id='fa-timeline-graph',
        config={'displayModeBar': False}, responsive=True,
        figure=fig,
        style={"flex": 1}
    )
], p=10, style={"flex": 1})


@callback(
    Output("fa-timeline-graph", "figure", allow_duplicate=True),
    Input("fa-timeline-carousel1", "active"),
    Input("fa-timeline-carousel2", "active"),
    Input("fa-timeline-total-chk", "checked"),
    Input("fa-timeline-stack-chk", "checked"),
    Input("fa-grid", "virtualRowData"),
    State("fa-timeline-graph", "figure"),
    prevent_initial_call=True
)
def update_fa_timeline_data(carousel1, carousel2, total, stack, virtual_data, fig):
    patched_fig = Patch()
    if not virtual_data:
        for i, trace in enumerate(fig['data']):
            patched_fig["data"][i]['x'] = None
            patched_fig["data"][i]['y'] = None
        return patched_fig

    dff_grid = pd.DataFrame(virtual_data)

    # get the col name from the carousel index
    col = list(cat_cols.keys())[carousel2]

    # get the sum financing and nb of project by board meeting and selected col
    dff = dff_grid.groupby([col, 'BM'])['FA Financing'].sum().reset_index()
    group_sizes = dff_grid.groupby([col, 'BM']).size().reset_index(name='Number')
    dff = pd.merge(dff, group_sizes, on=[col, 'BM'])
    # get the full range of board meetings
    boards = pd.Series(range(dff['BM'].min(), dff['BM'].max() + 1), name='BM')
    # transform bool to yes/no
    if col == 'Priority State':
        dff[col] = dff[col].apply(lambda x: 'Priority States' if x else 'Not Priority States')
    if col == 'Multiple Countries':
        dff[col] = dff[col].apply(lambda x: 'Multiple Countries Projects' if x else 'Single Country Projects')
    # get the total by board meeting
    dff_total = dff_grid.groupby('BM')['FA Financing'].sum().reset_index()
    group_sizes_total = dff_grid.groupby('BM').size().reset_index(name='Number')
    dff_total = pd.merge(dff_total, group_sizes_total, on='BM')
    # add the missing boards
    boards_total = pd.Series(range(dff_total['BM'].min(), dff_total['BM'].max() + 1), name='BM')
    dff_total = pd.merge(boards_total, dff_total, on='BM', how='left').fillna(value=0).sort_values('BM')
    dff_total['Number'] = dff_total['Number'].astype(int)
    # get the cumsum of financing and number
    dff_total['cum-sum'] = dff_total['FA Financing'].cumsum()
    dff_total['cum-num'] = dff_total['Number'].cumsum()

    # as the number of traces (=cat) is not the same for each col,
    # we generate a new fig and keep only the 'data' to patch the current fig, so that we keep the layout def
    data_fig = go.Figure()
    for cat in cat_cols[col]:
        # merge with Board series to add the missing boards for that cat, add 0 for missing boards and
        # sort by BM to be sure there are ordered for the cumulated sum
        df_cat = pd.merge(boards, dff[dff[col] == cat], on='BM', how='left').fillna(value=0).sort_values('BM')
        df_cat['Number'] = df_cat['Number'].astype(int)
        # get the cumsum of financing and number and their percentage
        df_cat['cum-sum'] = df_cat['FA Financing'].cumsum()
        df_cat['cum-sum %'] = df_cat['cum-sum'] / dff_total['cum-sum']
        df_cat['cum-num'] = df_cat['Number'].cumsum()
        df_cat['cum-num %'] = df_cat['cum-num'] / dff_total['cum-num']

        # carousel1 0=Financing 1=Number
        if carousel1:
            y = df_cat['cum-num']
            texttemplate = "%{text}"
            customdata = list(zip(df_cat['cum-sum'], df_cat['cum-num %']))
            hovertemplate = '<b>%{y}</b> (%{customdata[0]:$.4s})<br>%{customdata[1]:.0%} of Total'
        else:
            y = df_cat['cum-sum']
            texttemplate = "%{text:$.4s}"
            customdata = list(zip(df_cat['cum-num'], df_cat['cum-sum %']))
            hovertemplate = '<b>%{y:$.4s}</b> (%{customdata[0]})<br>%{customdata[1]:.0%} of Total'

        data_fig.add_scatter(
            name=cat,
            mode='lines+markers+text',
            x=df_cat['BM'],
            y=y,
            stackgroup='one' if stack else None,
            line={'color': cat_cols[col][cat], 'width': 3},
            marker={'size': 10, 'opacity': [0] * (len(df_cat) - 1) + [1]},
            text=[''] * (len(df_cat) - 1) + [y.iloc[-1]],
            textposition="middle right", texttemplate=texttemplate,
            textfont={'size': 14, 'color': cat_cols[col][cat], 'weight': "bold"},
            customdata=customdata, hovertemplate=hovertemplate,
        )

    # add total if selected
    if total:
        # carousel1 0=Financing 1=Number
        if carousel1:
            y = dff_total['cum-num']
            texttemplate = "%{text}"
            customdata = dff_total['cum-sum']
            hovertemplate = '<b>%{y}</b> (%{customdata:$.4s})'
        else:
            y = dff_total['cum-sum']
            texttemplate = "%{text:$.4s}"
            customdata = dff_total['cum-num']
            hovertemplate = '<b>%{y:$.4s}</b> (%{customdata})'

        data_fig.add_scatter(
            name='Total',
            mode='lines+markers+text',
            x=dff_total['BM'],
            y=y,
            line={'color': total_color, 'width': 3},
            marker={'size': 10, 'opacity': [0] * (len(dff_total) - 1) + [1]},
            text=[''] * (len(dff_total) - 1) + [y.iloc[-1]],
            textposition="middle left", texttemplate=texttemplate,
            textfont={'size': 14, 'color': total_color, 'weight': "bold"},
            customdata=customdata, hovertemplate=hovertemplate,
        )

    patched_fig["data"] = data_fig["data"]
    patched_fig["layout"]["yaxis"]["title"]["text"] = 'Number of Projects' if carousel1 else 'Financing'
    patched_fig["layout"]["yaxis"]["tickprefix"] = None if carousel1 else '$'

    return patched_fig


@callback(
    Output("fa-timeline-graph", "figure"),
    Input("color-scheme-switch", "checked"),
)
def update_figure_theme(checked):
    patched_fig = Patch()
    patched_fig["layout"]["template"] = pio.templates[f"mantine_{'light' if checked else 'dark'}"]
    return patched_fig
