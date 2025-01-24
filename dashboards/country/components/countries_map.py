# dasd

# fig = go.Figure()
#
#
# fig.add_choropleth(
#     locations=df['ISO3'],
#     z=df['FA Financing $'],
#     # colorscale='Viridis',
#     # colorbar_tickprefix='$',
#     # text=df['COUNTRY'],
#     # autocolorscale=False,
#     # reversescale=True,
#     # marker_line_color='darkgray',
#     # marker_line_width=0.5,
#     # colorbar_title='GDP<br>Billions US$',
# )
#
# fig.update_layout(
#     margin={"r": 0, "t": 0, "l": 0, "b": 0},
#     # paper_bgcolor='rgba(0,0,0,0)',
#     # plot_bgcolor='rgba(0,0,0,0)',
#     #
#     # geo=dict(
#     #     bgcolor='rgba(0,0,0,0)',
#     #     showframe=False,
#     #     showlakes=False,
#     #     showcountries=True,
#     #
#     # ),
# )
#
# map_graph = html.Div([
#     dcc.Graph(
#         id='example-graph',
#         responsive=True,
#         config={'displayModeBar': False},
#         figure=fig,
#         className='h-100 flex-fill'
#     )
# ], className='h-100 flex-fill d-flex flex-column gap-2')
#
# layout_countries = html.Div([
#
#     dbc.Card([
#         dbc.CardHeader(" Map", className='fs-5 text-body text-center'),
#         dbc.CardBody(map_graph, className='p-2'),
#     ], className='h-50'),
#
#     html.Div([
#         html.Div("The grid can be used to filter the data of the map"),
#         # people_grid
#     ], className='h-50 d-flex flex-column dbc dbc-ag-grid'),
#
# ], className='flex-fill d-flex flex-column gap-2 p-2 overflow-auto')