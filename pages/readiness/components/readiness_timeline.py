import os
from pprint import pprint
from datetime import timedelta, datetime

from dash import dcc, html, Input, Output, State, callback, no_update, clientside_callback, Patch, ctx
import dash_mantine_components as dmc
import plotly.graph_objects as go
import plotly.io as pio

import pandas as pd

from app_config import df_readiness, PRIMARY_COLOR, SECONDARY_COLOR

plotly_to_pandas_period = {
    'M12': 'YE',
    'M6': '2QE',
    'M3': 'QE',
    'M1': 'ME'
}
date_hovertemplate = {
    'GCF': '%{customdata}',
    'M12': '%{x|%Y}',
    'M6': '%{x|H%h, %Y}',
    'M3': '%{x|Q%q, %Y}',
    'M1': '%{x|%b, %Y}'
}


def set_time_xticks(xrange, agg_period):
    YEAR = timedelta(days=365)
    range_timedelta = xrange[1] - xrange[0]

    if 10 * YEAR <= range_timedelta or agg_period == 'M12':
        xticks = dict(dtick="M12", tickformat="%Y\n ", minor_dtick="M12")
    elif (6 * YEAR <= range_timedelta < 10 * YEAR) or agg_period == "M6":
        xticks = dict(dtick="M6", tickformat="H%h\n%Y", minor_dtick="M12")
    elif (3 * YEAR <= range_timedelta < 6 * YEAR) or agg_period == "M3":
        xticks = dict(dtick="M3", tickformat="Q%q\n%Y", minor_dtick="M12")
    else:
        xticks = dict(dtick="M1", tickformat="%b\nQ%q '%y", minor_dtick="M3")
    return xticks


agg_init = 'M3'

# sort by date to have the values in the correct order
dff = df_readiness.sort_values('Approved Date')
# add cumulated financing for the line
dff['Cumulative Financing'] = dff['Financing'].cumsum()
# aggregate for bar
df_timeline_agg = dff.set_index('Approved Date').resample(
    plotly_to_pandas_period[agg_init]).size().reset_index(name='Number')

fig = go.Figure()
fig.add_scatter(
    name='Financing',
    x=dff['Approved Date'],
    y=dff['Cumulative Financing'],
    mode='lines+markers+text',
    marker={'size': 10, 'opacity': [0] * (len(dff) - 1) + [1]},
    text=[''] * (len(dff) - 1) + [dff['Cumulative Financing'].iloc[-1]],
    textposition="top center", texttemplate="%{text:$.4s}",
    textfont={'color': PRIMARY_COLOR, 'weight': "bold", 'size': 14},
    hovertemplate='%{x|%b %d, %Y}<br><b>%{y:$.4s}</b><extra></extra>',
    zorder=2,  # display the line above the bars
    line={'color': PRIMARY_COLOR, 'width': 3}
)

fig.add_bar(
    name='Projects Number',
    x=df_timeline_agg['Approved Date'],
    y=df_timeline_agg['Number'],
    xperiod=agg_init,
    xperiodalignment="middle",
    yaxis='y2',
    textfont_color='var(--mantine-color-text)', textangle=0,
    hovertemplate=f'{date_hovertemplate[agg_init]}<br><b>%{{y}} Projects</b><extra></extra>',
    marker=dict(
        color='#97cd3f',
        line={'color': '#97cd3f', 'width': 2},
        # Trick to add transparency to the color marker only, not the border, as marker_opacity applies to both
        pattern={'fillmode': "replace", 'shape': "/", 'solidity': 1, 'fgcolor': '#97cd3f', 'fgopacity': 0.5}
    ),
)

# add the lines and annotations for the replenishment periods
GCF_periods = {
    'IRM': {'start': '2015-01-01', 'hover': 'Initial Resource Mobilization period<br>(2015-2019)'},
    'GCF-1': {'start': '2020-01-01', 'hover': 'GCF first replenishment period<br>(2020-2023)'},
    'GCF-2': {'start': '2024-01-01', 'hover': 'GCF second replenishment period<br>(2024-2027)'},
}

for i, period in enumerate(GCF_periods):

    fig.add_vline(visible=False, x=GCF_periods[period]['start'],  # type: ignore[type-var]
                  line={'color': "var(--mantine-color-text)", 'width': 3, 'dash': "dash"})

    if i < len(GCF_periods) - 1:
        next_period_start = GCF_periods[list(GCF_periods.keys())[i + 1]]['start']
    else:
        next_period_start = '2028-01-01'

    start_date = pd.to_datetime(GCF_periods[period]['start'])
    end_date = pd.to_datetime(next_period_start)
    middle_date = start_date + (end_date - start_date) / 2

    fig.add_annotation(
        visible=False, showarrow=False,
        x=middle_date,
        yref="y domain", yanchor="top", y=1,
        text=period,
        font={'size': 16, 'color': "var(--mantine-color-text)", 'weight': "bold", 'lineposition': "under"},
        hovertext=GCF_periods[period]['hover'],
    )

# add end of GCF-2
fig.add_vline(visible=False, x='2028-01-01',  # type: ignore[type-var]
              line={'color': "var(--mantine-color-text)", 'width': 3, 'dash': "dash"})

xaxis_range = [df_readiness['Approved Date'].min(), df_readiness['Approved Date'].max()]
xticks = set_time_xticks(xaxis_range, agg_init)

fig.update_xaxes(
    # showline=True, linewidth=2, linecolor='black',
    showgrid=False,
    ticklabelmode="period",
    ticks="inside",
    dtick=xticks["dtick"],
    tickformat=xticks["tickformat"],
    tickwidth=2,
    minor=dict(ticks="outside", dtick=xticks["minor_dtick"], tickwidth=2, ticklen=30),
)
yaxis = dict(
    title={'text': 'Financing', 'font_size': 16, 'font_weight': "bold"},
    showgrid=False, tickprefix='$', rangemode="tozero",
    # showline=True, linewidth=2, linecolor='black',
    # zeroline=True, zerolinecolor="black", zerolinewidth=2,
)
yaxis2 = dict(
    # showline=True, linewidth=2, mirror=True,
    title={'text': 'Number of Projects', 'font_size': 16, 'font_weight': "bold"},
    showgrid=False, rangemode="tozero", overlaying='y', side='right'
)
fig.update_layout(
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    legend=dict(
        xanchor="left", x=0.05,
        yanchor="top", y=0.95,
    ),
    barcornerradius=3,
    yaxis=yaxis, yaxis2=yaxis2,
)


def readiness_timeline(theme='light'):
    fig.update_layout(template=pio.templates[f"mantine_{theme}"])
    return dmc.Stack([
        dmc.Group(
            [
                'Project Number by',
                dmc.Select(
                    id="readiness-timeline-dropdown",
                    data=[
                        {"value": "M1", "label": "Month"},
                        {"value": "M3", "label": "Quarter"},
                        {"value": "M6", "label": "Half Year"},
                        {"value": "M12", "label": "Year"},
                        {"value": "GCF", "label": "GCF Replenishments"},
                    ],
                    value="M3",
                    checkIconPosition='right', w=150,
                    comboboxProps={'transitionProps': {'duration': 300, 'transition': 'scale-y'}},
                ),
                dmc.Checkbox(id="readiness-timeline-labels-chk", label="Show labels"),
                dmc.Checkbox(id="readiness-timeline-reple-lines-chk", label="Show Replenishments Periods"),
                dmc.Checkbox(
                    id="readiness-timeline-reple-split-chk",
                    w=200, label="Split Financing by Replenishments Periods",
                    styles={'body': {'align-items': 'center'}}
                ),
            ]
        ),

        dcc.Graph(
            id={'type': 'figure', 'subtype': 'line+bar', 'index': 'readiness-timeline'},
            config={'displayModeBar': False}, responsive=True,
            figure=fig,
            style={"flex": 1}
        )
    ], p=10, style={"flex": 1}
    )


@callback(
    Output({'type': 'figure', 'subtype': 'line+bar', 'index': 'readiness-timeline'}, 'figure', allow_duplicate=True),
    Input('readiness-timeline-dropdown', 'value'),
    Input('readiness-timeline-reple-split-chk', 'checked'),
    Input({'type': 'grid', 'index': 'readiness'}, "virtualRowData"),
    prevent_initial_call=True,
)
def update_data(agg, split_line, virtual_data):
    # empty figure if there is no data in the grid
    patched_fig = Patch()
    if not virtual_data:
        patched_fig["data"][0].update({'x': None, 'y': None})
        patched_fig["data"][1].update({'x': None, 'y': None})
        return patched_fig

    dff = pd.DataFrame(virtual_data)
    # convert back from date string from the grid to datetime
    dff['Approved Date'] = pd.to_datetime(dff['Approved Date'])
    dff.sort_values('Approved Date', inplace=True)  # sort by date to have the values in the correct order
    dff['Cumulative Financing'] = dff['Financing'].cumsum()  # add cumulated financing for the line

    # Line patch
    if split_line:
        x_data, y_data, marker_opacity, text_data = [], [], [], []

        bins = [datetime(2015, 1, 1), datetime(2020, 1, 1), datetime(2024, 1, 1), datetime(2028, 1, 1)]

        for i in range(len(bins) - 1):
            mask = (dff['Approved Date'] >= bins[i]) & (dff['Approved Date'] < bins[i + 1])
            period_data = dff.loc[mask].copy()  # Creating a copy to avoid SettingWithCopyWarning
            period_data['Cumulative Financing'] = period_data['Financing'].cumsum()
            x_data += period_data['Approved Date'].tolist() + [None]
            y_data += period_data['Cumulative Financing'].tolist() + [None]
            marker_opacity += [0] * (len(period_data) - 1) + [1, None]
            text_data += [''] * (len(period_data) - 1) + [period_data['Cumulative Financing'].iloc[-1]] + [None]

        patched_fig["data"][0].update(dict(
            x=x_data, y=y_data, marker={'opacity': marker_opacity}, text=text_data,
        ))

    else:
        patched_fig["data"][0].update(dict(
            x=dff['Approved Date'], y=dff['Cumulative Financing'],
            marker={'opacity': [0] * (len(dff) - 1) + [1]},
            text=[''] * (len(dff) - 1) + [dff['Cumulative Financing'].iloc[-1]],
        ))

    # bar patch
    if agg == 'GCF':
        # As the periods are not constant, we can't use xperiod, so will use custom bar width and custom x
        bins = [datetime(2015, 1, 1), datetime(2020, 1, 1), datetime(2024, 1, 1), datetime(2028, 1, 1)]
        widths = [(bins[i + 1] - timedelta(days=1) - bins[i]).total_seconds() * 1000 * 0.95 for i in
                  range(len(bins) - 1)]
        period_middles = [bins[i] + (bins[i + 1] - timedelta(days=1) - bins[i]) / 2 for i in range(len(bins) - 1)]
        # will assign the middle date on each row in the corresponding period
        dff['Middle Date'] = pd.cut(dff['Approved Date'], bins=bins, labels=False, right=False).map(
            dict(enumerate(period_middles)))
        # Group by the custom periods and count the occurrences to have the number of projects
        dff_agg = dff.groupby('Middle Date').size().reset_index(name='Number')
        # rename the col to use it as x below
        dff_agg = dff_agg.rename(columns={'Middle Date': 'Approved Date'})

        patched_fig["data"][1]['width'] = widths
        # remove the xperiod to not mess with the bar offset
        patched_fig["data"][1]['xperiod'] = None
        # add customdata for hover text
        patched_fig["data"][1]['customdata'] = ['IRM (2015-2019)', 'GCF-1 (2020-2023)', 'GCF-2 (2024-2027)']
        # adjust the y range for a better view
        patched_fig["layout"]["yaxis2"]['autorange'] = False
        patched_fig["layout"]["yaxis2"]['range'] = [0, 500]
    else:
        dff_agg = dff.set_index('Approved Date').resample(
            plotly_to_pandas_period[agg]).size().reset_index(name='Number')
        patched_fig["data"][1]['xperiod'] = agg
        # remove the custom width and y range if set previously selecting agg='GCF'
        patched_fig["data"][1]['width'] = None
        patched_fig["layout"]["yaxis2"]['autorange'] = True

    patched_fig["data"][1].update(dict(
        x=dff_agg['Approved Date'],
        y=dff_agg['Number'],
        hovertemplate=f'{date_hovertemplate[agg]}<br><b>%{{y}} Projects</b><extra></extra>'
    ))

    return patched_fig


@callback(
    Output({'type': 'figure', 'subtype': 'line+bar', 'index': 'readiness-timeline'}, 'figure', allow_duplicate=True),
    Input({'type': 'figure', 'subtype': 'line+bar', 'index': 'readiness-timeline'}, 'relayoutData'),  # Triggered by zooming/panning on figure
    Input('readiness-timeline-dropdown', 'value'),
    State({'type': 'figure', 'subtype': 'line+bar', 'index': 'readiness-timeline'}, 'figure'),
    prevent_initial_call=True,
)
def update_xticks(_, agg, fig):
    # NOTE: we use the fig to have the xrange, as relayout_data may not have it

    # no update if no date format for x axis, like having no data in grid
    if not isinstance(fig["layout"]["xaxis"]["range"][0], str):
        return no_update

    xaxis_range = [datetime.fromisoformat(fig["layout"]["xaxis"]["range"][0]),
                   datetime.fromisoformat(fig["layout"]["xaxis"]["range"][1])]
    xticks = set_time_xticks(xaxis_range, agg)

    patched_fig = Patch()

    patched_fig["layout"]["xaxis"].update(dict(
        dtick=xticks["dtick"],
        tickformat=xticks["tickformat"],
        minor_dtick=xticks["minor_dtick"],
    ))
    return patched_fig


@callback(
    Output({'type': 'figure', 'subtype': 'line+bar', 'index': 'readiness-timeline'}, 'figure', allow_duplicate=True),
    Input('readiness-timeline-labels-chk', 'checked'),
    prevent_initial_call=True
)
def toggle_bar_labels(checked):
    patched_fig = Patch()
    patched_fig["data"][1]['texttemplate'] = '%{y}' if checked else None
    return patched_fig


@callback(
    Output({'type': 'figure', 'subtype': 'line+bar', 'index': 'readiness-timeline'}, 'figure', allow_duplicate=True),
    Input('readiness-timeline-reple-lines-chk', 'checked'),
    State({'type': 'figure', 'subtype': 'line+bar', 'index': 'readiness-timeline'}, 'figure'),
    prevent_initial_call=True
)
def toggle_replenishment_visibility(checked, fig):
    patched_fig = Patch()
    # Toggle vlines
    for i, shape in enumerate(fig["layout"]["shapes"]):
        patched_fig["layout"]["shapes"][i]['visible'] = checked
    # Toggle annotations
    for i, annotation in enumerate(fig["layout"]["annotations"]):
        patched_fig["layout"]["annotations"][i]['visible'] = checked

    return patched_fig
