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
import dash_ag_grid as dag

import pandas as pd

from app_config import df_entities, PRIMARY_COLOR, format_money_number_si

dff = df_entities.copy()
dff['DAE'] = dff['DAE'].apply(
    lambda x: 'Direct Access Entities (DAE)' if x else 'International Accredited Entities (IAE)')


def create_treemap_data(df, levels):
    """
    Create treemap data dictionary from a dataframe and specified hierarchy levels.
    Validates levels and handles errors gracefully.
    """
    # Validate levels
    if any(level not in df.columns for level in levels):
        raise ValueError("One or more levels are not present in the DataFrame.")
    if df.empty:
        return {key: [] for key in ['ids', 'labels', 'parents', 'entities', 'sum_financing', 'sum_number']}

    treemap_data = {
        'ids': ['Overall'],
        'labels': ['Overall'],
        'parents': [''],
        'counts': [len(df)],
        'sum_financing': [df['FA Financing'].sum()],
        'sum_number': [df['# Approved'].sum()]
    }

    def build_hierarchy(df, current_level=0, parent_ids=""):
        if current_level < len(levels):
            level_values = df[levels[current_level]].unique()
            if len(level_values) == 0:  # Handle empty level
                return

            for value in level_values:
                current_id = f"{parent_ids}/{value}"
                df_current_value = df[df[levels[current_level]] == value]

                # Only add node if it has data
                if len(df_current_value) > 0:
                    treemap_data['ids'].append(current_id)
                    treemap_data['labels'].append(value)
                    treemap_data['parents'].append(parent_ids)
                    treemap_data['counts'].append(len(df_current_value))
                    treemap_data['sum_financing'].append(df_current_value['FA Financing'].sum())
                    treemap_data['sum_number'].append(df_current_value['# Approved'].sum())

                    build_hierarchy(df_current_value, current_level + 1, current_id)

    build_hierarchy(df, parent_ids="Overall")

    # Ensure we have at least one node besides root
    if len(treemap_data['ids']) <= 1:
        return {key: [] for key in treemap_data.keys()}  # Return empty structure

    return treemap_data


treemap_data = create_treemap_data(dff, levels=['DAE', 'Type', 'Sector', 'Size'])

fig = go.Figure()
fig.add_treemap(
    ids=treemap_data['ids'],
    labels=treemap_data['labels'],
    parents=treemap_data['parents'],
    values=treemap_data['counts'],
    branchvalues='total',
    marker_cornerradius=5,
    customdata=list(zip(
        treemap_data['counts'],
        treemap_data['sum_number'],
        # use custom function to have $1B instead of $1G, as it is not possible with D3-formatting
        [format_money_number_si(val) for val in treemap_data['sum_financing']]
    )),
    texttemplate='<span style="font-size: 1.2em"><b>%{label} - %{customdata[0]} Entities</b></span><br>',
    hovertemplate=(
        '%{currentPath}<br><br>'
        '<span style="font-size: 1.2em"><b>%{label} - %{customdata[0]} Entities</b></span><br>'),
)

fig.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin={"r": 0, "t": 20, "l": 0, "b": 0},
    treemapcolorway=["#15a14a", "#1569a1"],
)


def entities_treemap(theme='light'):
    fig.update_layout(template=pio.templates[f"mantine_{theme}"])
    return dmc.Group([
        dmc.Stack([
            dmc.NumberInput(
                id="entities-treemap-max-depth-input",
                label="Level Depth: ",
                min=1, max=5, value=5,
                size="xs", w=120,
                styles={'input': {'textAlign': 'center', 'fontSize': 14}},
            ),
            dmc.Select(
                id="entities-treemap-values-select",
                label="Size by:",
                data=[
                    {"label": "# Entity", "value": "counts"},
                    {"label": "FA Number", "value": "sum_number"},
                    {"label": "FA Financing", "value": "sum_financing"},
                ],
                value="counts",
                checkIconPosition="right", size="xs", w=120,
            ),
            dmc.Checkbox(id="entities-treemap-more-chk", label="More Info"),
            dag.AgGrid(
                id={'type': 'grid', 'index': 'entities-levels-drag'},
                rowData=[{'level': 'DAE'}, {'level': 'Type'}, {'level': 'Sector'}, {'level': 'Size'}],
                columnDefs=[{'field': 'level', 'headerName': 'Levels Order', 'rowDrag': True}],
                defaultColDef={'sortable': False, "resizable": False},
                columnSize="sizeToFit",
                dashGridOptions={"rowDragManaged": True, "rowHeight": 30, 'headerHeight': 30},
                className=f"ag-theme-quartz{'' if theme == 'light' else '-dark'}",
                style={"height": 153, "width": 120}
            ),
        ], justify='space-around'),
        dcc.Graph(
            id={'type': 'figure', 'subtype': 'treemap', 'index': 'entities'},
            config={'displayModeBar': False}, responsive=True,
            figure=fig,
            style={"flex": 1},
        )
    ], p=10, align='stretch', style={"flex": 1})


@callback(
    Output({'type': 'figure', 'subtype': 'treemap', 'index': 'entities'}, "figure", allow_duplicate=True),
    Input({'type': 'grid', 'index': 'entities'}, "virtualRowData"),
    Input("entities-treemap-values-select", "value"),
    Input({'type': 'grid', 'index': 'entities-levels-drag'}, "virtualRowData"),
    prevent_initial_call=True
)
def update_tree_data(virtual_data, selected_value, virtual_data_level):
    patched_fig = Patch()
    if not virtual_data:
        patched_fig["data"][0].update({
            'ids': [], 'labels': [], 'parents': [],
            'values': [], 'text': [], 'customdata': []
        })
        return patched_fig

    dff = pd.DataFrame(virtual_data)
    dff['DAE'] = dff['DAE'].apply(
        lambda x: 'Direct Access Entities (DAE)' if x else 'International Accredited Entities (IAE)')

    levels_order = [row['level'] for row in virtual_data_level]
    treemap_data = create_treemap_data(dff, levels=levels_order)

    patched_fig["data"][0].update(dict(
        ids=treemap_data['ids'],
        labels=treemap_data['labels'],
        parents=treemap_data['parents'],
        values=treemap_data[selected_value],
        customdata=list(zip(
            treemap_data['counts'],
            treemap_data['sum_number'],
            # use custom function to have $1B instead of $1G, as it is not possible with D3-formatting
            [format_money_number_si(val) for val in treemap_data['sum_financing']],
        ))
    ))

    # change the colorway depending on the number of cat
    if levels_order[0] in ['DAE', 'Sector']:
        patched_fig["layout"]["treemapcolorway"] = ["#15a14a", "#1569a1"]
    elif levels_order[0] == 'Type':
        patched_fig["layout"]["treemapcolorway"] = ["#15a14a", '#158575', "#1569a1"]
    else:
        patched_fig["layout"]["treemapcolorway"] = ["#15a14a", '#158575', '#2980b9', "#1569a1"]

    return patched_fig


@callback(
    Output({'type': 'figure', 'subtype': 'treemap', 'index': 'entities'}, "figure", allow_duplicate=True),
    Input("entities-treemap-max-depth-input", "value"),
    prevent_initial_call=True
)
def update_max_level(value):
    patched_fig = Patch()
    patched_fig["data"][0]["maxdepth"] = value
    return patched_fig


@callback(
    Output({'type': 'figure', 'subtype': 'treemap', 'index': 'entities'}, "figure", allow_duplicate=True),
    Input("entities-treemap-values-select", "value"),
    Input("entities-treemap-more-chk", "checked"),
    prevent_initial_call=True
)
def update_text_hover_info(selected_value, show_more):
    patched_fig = Patch()

    template_value = (
        '%{customdata[0]} Entities' if selected_value == "counts" else
        '%{customdata[1]} FA Number' if selected_value == "sum_number" else
        '%{customdata[2]} FA Financing'
    )

    template = f'<span style="font-size: 1.2em"><b>%{{label}} - {template_value}</b></span><br>'

    if show_more:
        template_custom1 = (
            'FA Number: <b>%{customdata[1]}</b>' if selected_value == "counts" else
            'Entities: <b>%{customdata[0]}</b>'
        )

        template_custom2 = (
            'FA Number: <b>%{customdata[1]}</b>' if selected_value == "sum_financing" else
            'FA Financing: <b>%{customdata[2]}</b>'
        )

        template += (
            '<i>%{percentParent:.1%} of parent (%{parent})<br>'
            '%{percentRoot:.1%} of total</i><br><br>'
            f'{template_custom1}<br>'
            f'{template_custom2}'
        )

    patched_fig["data"][0].update(dict(
        texttemplate=template,
        hovertemplate='%{currentPath}<br><br>' + template + '<extra></extra>'
    ))
    return patched_fig
