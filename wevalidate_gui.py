# Run this app with `python wevalidate_gui.py` and
# visit http://127.0.0.1:8088/ in your web browser.
import base64
import datetime
import io
import os

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from dash import Dash, html, dcc, Input, Output, State, Patch, MATCH, ALL, ctx
from dash.exceptions import PreventUpdate
import yaml
import pathlib

from validate import compare
from tools import eval_tools

app = Dash(external_stylesheets=[dbc.themes.DARKLY])


# noinspection PyPackageRequirements,PyPackageRequirements
def _build_dataset_form(type, n):
    openicon = 'images/open.gif'
    open_icon = base64.b64encode(open(openicon, 'rb').read())
    return html.Div(children=[
                                    html.Div(children=[
                                        html.H6('Name:', style={'margin-left': 128, 'vertical-align': 'middle', 'width': 92}),
                                        dcc.Input(placeholder="Name of the data set used in naming dataframe columns",
                                                  id={"type": type, "parameter": "data-name", "index": n},
                                                  style={'vertical-align': 'middle', 'width': 500},
                                                  required=True)
                                    ],
                                        style={'display': 'flex', 'margin-top': 5, 'margin-bottom': 5}),
                                    html.Div(children=[
                                        html.H6('Data Path:', style={'margin-left': 100, 'vertical-align': 'middle', 'width': 120}),
                                        dcc.Input(placeholder="Data File Full Path",
                                                  id={"type": type, "parameter": "file-path", "index": n},
                                                  style={'vertical-align': 'middle', 'width': 500},
                                                  required=True),
                                        dcc.Upload(
                                            html.A(
                                                html.Img(src='data:image/gif;base64,{}'.format(open_icon.decode()),
                                                         style={'vertical-align': 'middle', 'width': '25px', 'height': '25px'})),
                                            id={"type": type, "parameter": "file-selection", "index": n},
                                            multiple=True,
                                            style={'margin-left': 10, 'vertical-align': 'middle'}),
                                        dcc.Store(id={"type": type, "parameter": "file-content", "index": n})
                                    ],
                                        style={'display': 'flex', 'margin-top': 5, 'margin-bottom': 5}),
                                    # html.Div(children=[
                                    #     html.H6('Data Processing Function:', style={'margin-left': 50, 'text-align': 'right', 'width': 123}),
                                    #     dcc.Input(placeholder="If using csv files, no need to change this input",
                                    #               id={"type": type, "parameter": "function", "index": n},
                                    #               value='csv',
                                    #               style={'margin-left': 47, 'margin-top': 8, 'vertical-align': 'middle', 'width': 500, 'height': 30},
                                    #               required=True)
                                    # ],
                                    #     style={'display': 'flex', 'margin-top': 5, 'margin-bottom': 5}),
                                    html.Div(children=[
                                        html.H6('Variable Name:', style={'margin-left': 67, 'vertical-align': 'middle', 'width': 153}),
                                        dcc.Input(placeholder="Must match column header in csv file",
                                                  id={"type": type, "parameter": "var-name", "index": n},
                                                  style={'vertical-align': 'middle', 'width': 500},
                                                  required=True)
                                    ],
                                        style={'display': 'flex', 'margin-top': 5, 'margin-bottom': 5}),
                                    html.Div(children=[
                                        html.H6('Frequency (min):', style={'margin-left': 57, 'vertical-align': 'middle', 'width': 163}),
                                        dcc.Input(placeholder="Data frequency in minutes",
                                                  id={"type": type, "parameter": "frequency", "index": n},
                                                  value=60,
                                                  style={'vertical-align': 'middle', 'width': 500},
                                                  required=True)
                                    ],
                                        style={'display': 'flex', 'margin-top': 5, 'margin-bottom': 5}),
                                    html.Div(children=[
                                        html.H6('Flag:', style={'margin-left': 140, 'vertical-align': 'middle', 'width': 80}),
                                        dcc.Input(placeholder="Converts flagged values to NaNs",
                                                  id={"type": type, "parameter": "flag", "index": n},
                                                  value=999,
                                                  style={'vertical-align': 'middle', 'width': 500},
                                                  required=True)
                                    ],
                                        style={'display': 'flex', 'margin-top': 5, 'margin-bottom': 5})
                                ])


def _run_gui(debug=True, port=8088):
    # openicon = 'images/open.gif'
    # open_icon = base64.b64encode(open(openicon, 'rb').read())
    plotly_template = pio.templates["plotly_dark"]
    # print(plotly_template)

    pio.templates["plotly_dark_custom"] = pio.templates["plotly_dark"]

    pio.templates["plotly_dark_custom"].update({'layout': {
        'font': {'color': '#aaa'},
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'geo': {'bgcolor': 'rgba(0,0,0,0)',
                'lakecolor': 'rgba(0,0,0,0)',
                'landcolor': 'rgba(0,0,0,0)',
                'showlakes': True,
                'showland': True,
                'subunitcolor': '#506784'},
    }})
    pio.templates.default = "plotly_dark_custom"
    tab_style = {
        'backgroundColor': '#222',
        'borderTop': '1px solid #222',
        'borderLeft': '1px solid #222',
        'borderRight': '1px solid #222',
        'borderBottom': '0.1px solid grey',
        'padding': '0px',
        'fontWeight': 'bold',
    }

    tab_selected_style = {
        'borderTop': '3px solid #119DFF',
        'borderBottom': '1px solid #222',
        'borderLeft': '1px solid #222',
        'borderRight': '1px solid #222',
        'backgroundColor': 'black',
        'color': 'WhiteSmoke',
        'padding': '6px'
    }

    app.title = "We Validate"
    app.layout = dbc.Container(
        [
            # html.Div(
            html.H2("WeValidate GUI",
                    style={'color': 'WhiteSmoke', 'vertical-align': 'middle',
                           'word-spacing': '15px', 'textAlign': 'center', 'margin-bottom': 0}),
            html.Hr(style={'margin-top': 0}),
            #     style={'textAlign': 'center'}
            # ),
            # html.Div(
                # children=[
                    # html.Div(
                    #     html.Img(src='data:image/png;base64,{}'.format(iarpea.decode()), style={'height': '25px'}),
                    #     style={'flex': "10%", 'padding-top': '20px', 'textAlign': 'left'}
                    # ),
            html.Details([
                html.Summary(
                    # html.Div(children=[
                    #     html.H4("Configurations",
                    #             style={'display': 'inline-block', 'color': 'WhiteSmoke', 'vertical-align': 'middle',
                    #                    'word-spacing': '15px'}),
                    #     html.Button('Load A Configuration',
                    #              id='load-configuration',
                    #              n_clicks=0,
                    #              style={'vertical-align': 'top', 'margin-left': 80, 'margin-top': 0, 'border-radius': 8, 'height': 25})
                    # ], style={'display': 'flex', 'margin-bottom': 5}),
                    # dbc.Col([
                    #     html.H4("Configurations",
                    #             style={'display': 'inline-block', 'color': 'WhiteSmoke', 'vertical-align': 'middle',
                    #                    'word-spacing': '15px'}),
                    #     html.Button('Load A Configuration',
                    #              id='load-configuration',
                    #              n_clicks=0,
                    #              style={'vertical-align': 'top', 'margin-left': 120, 'margin-top': 0, 'border-radius': 8, 'height': 20})
                    #
                    # ]),
                    html.H4("Configurations",
                            style={'display': 'inline-block', 'color': 'WhiteSmoke', 'vertical-align': 'middle',
                                   'word-spacing': '15px'})
                ),
                dbc.Row([
                    dbc.Tooltip('Please drag and drop or select a configuration yml file to run We-Validate, or fill the configuration '
                                'form below and click the "Run WeValidate" button.',
                                target="upload-config-div",
                                placement='left-end'),
                    # dcc.Tooltip('Please drag and drop or select a configuration yml file or fill the configuration '
                    #             'form below'),
                    # html.Button('Load a Configuration',
                    #             id='load-configuration',
                    #             n_clicks=0,
                    #             title='Load a configuration yml file to auto fill the form',
                    #             style={'vertical-align': 'middle', 'margin-left': 30, 'margin-top': 10, 'margin-bottom': 20, 'border-radius': 8, 'height': 35, 'width': 180}),
                    dcc.Upload(
                        children=html.Div([
                            'Drag and Drop or ',
                            html.A('Select a Files ', style={'font-weight': 'bolder', 'cursor': 'pointer'}),
                            'to Run We-Validate, or Fill the Form Below and Click the Run WeValidate Button'
                        ], style={'font-size': 20, 'word-spacing': '3px', 'display': 'inline'}, id='upload-config-div'),

                        id='configuration-upload',
                        multiple=False,
                        style={'margin-bottom': 15,
                               'width': '100%',
                               'height': '60px',
                               'lineHeight': '60px',
                               'borderWidth': '1px',
                               'borderStyle': 'dashed',
                               'borderRadius': '5px',
                               'textAlign': 'center'}),
                    dcc.Store(id='configuration')]
                ),
                dbc.Row([
                    dbc.Col([
                        html.Div(children=[
                            html.H5('Time Window:', style={'margin-left': 20, 'vertical-align': 'middle', 'width': 200}),
                            html.Label('Start', style={'vertical-align': 'middle'}),
                            dcc.Input(id='start-time', type="datetime-local", step="300", required=True, style={'margin-left': 20, 'vertical-align': 'middle'}),
                            html.Label('End', style={'margin-left': 40, 'vertical-align': 'middle'}),
                            dcc.Input(id='end-time', type="datetime-local", step="300", required=True, style={'margin-left': 20, 'vertical-align': 'middle'}),
                            # dash_datetimepicker.DashDatetimepicker(utc=True)
                        ], style={'display': 'flex', 'margin-bottom': 5}),
                        html.Div(children=[
                            html.H5('Metrics:', style={'margin-left': 20, 'vertical-align': 'middle', 'width': 200}),
                            dcc.Dropdown(['rmse', 'crmse', 'bias', 'bias_pct', 'mae', 'mae_pct', 'cross_correlation'],
                                         multi=True,
                                         id='metrics',
                                         placeholder="Select at least one metric to be calculated and plotted",
                                         style={'vertical-align': 'middle', 'width': 500, 'color': 'black'})
                        ], style={'display': 'flex', 'margin-top': 5, 'margin-bottom': 5}),
                        html.Div(children=[
                            html.H5('Output Directory:', style={'margin-left': 20, 'vertical-align': 'middle', 'width': 200}),
                            dcc.Input(placeholder="Output Directory Path", id='output-dir',
                                      style={'vertical-align': 'middle', 'width': 500}),
                            # dcc.Input(type='file', style={'webkitdirectory': 'true'}),
                            # < input type = "file", id = "filepicker" name = "fileList" webkitdirectory multiple / >
                            # dcc.Upload(
                            #     html.A(
                            #         html.Img(src='data:image/gif;base64,{}'.format(open_icon.decode()),
                            #                  style={'vertical-align': 'middle', 'width': '25px', 'height': '25px'})),
                            #     style={'margin-left': 10, 'vertical-align': 'middle'})
                        ], style={'display': 'flex', 'margin-top': 5, 'margin-bottom': 5}),
                        html.Div(children=[
                            html.H5('Name of The Run:', style={'margin-left': 20, 'vertical-align': 'middle', 'width': 200}),
                            dcc.Input(placeholder="name of the run appended to the name of any saved files",
                                      id='run-name',
                                      style={'vertical-align': 'middle', 'width': 500},
                                      required=True)
                        ], style={'display': 'flex', 'margin-top': 5, 'margin-bottom': 5}),
                        html.Div(children=[
                            html.H5('Baseline Data Set:', style={'margin-left': 20, 'vertical-align': 'middle'}),
                            _build_dataset_form('base', 0),
                        ], style={'margin-top': 45, 'margin-bottom': 5}),
                    ],
                        width=6),
                    dbc.Col([
                        html.Div(children=[
                            html.H5('Reference:', style={'margin-left': 80, 'vertical-align': 'middle'}),
                            html.Div(children=[
                                html.H6('Variable Name:', style={'margin-left': 67, 'vertical-align': 'middle', 'width': 153}),
                                dcc.Input(placeholder="Variable name that displays on plots",
                                          id='ref-var-name',
                                          style={'vertical-align': 'middle', 'width': 500},
                                          required=True)
                            ],
                                style={'display': 'flex', 'margin-top': 5, 'margin-bottom': 5}),
                            html.Div(children=[
                                html.H6('Variable Unit:', style={'margin-left': 78, 'vertical-align': 'middle', 'width': 142}),
                                dcc.Input(placeholder="Variable units that displays on plots",
                                          id='ref-var-unit',
                                          style={'vertical-align': 'middle', 'width': 500},
                                          required=True)
                            ],
                                style={'display': 'flex', 'margin-top': 5, 'margin-bottom': 5}),
                        ], style={'margin-top': 0}),
                        html.Div(
                            children=[
                                 html.Div(children=[
                                     html.H5('Compare Data Set(s):', style={'margin-left': 0, 'vertical-align': 'middle', 'width': 230}),
                                     html.Button('Add A Dataset',
                                                 id='add-data',
                                                 n_clicks=0,
                                                 style={'vertical-align': 'top', 'margin-top': 0, 'border-radius': 8, 'height': 30})
                                 ],
                                     style={'display': 'flex'}),
                                 html.Div(id='comp-config',
                                          children=[],
                                          style={'maxHeight': 250, "overflow": "scroll", 'margin-top': 0})
                            ], style={'margin-top': 95, 'margin-bottom': 5})
                    ],
                        width=6)]
                ),
                # html.Div(children=[
                #     html.Div(children=[
                #         html.H5('Time Window:', style={'margin-left': 20, 'vertical-align': 'middle', 'width': 200}),
                #         html.Label('Start', style={'vertical-align': 'middle'}),
                #         dcc.Input(type="datetime-local", step="60", required=True, style={'margin-left': 20, 'vertical-align': 'middle'}),
                #         html.Label('End', style={'margin-left': 40, 'vertical-align': 'middle'}),
                #         dcc.Input(type="datetime-local", step="1", required=True, style={'margin-left': 20, 'vertical-align': 'middle'}),
                #         # dash_datetimepicker.DashDatetimepicker(utc=True)
                #     ], style={'display': 'flex', 'margin-bottom': 5}),
                #     html.Div(children=[
                #         html.H5('Metrics:', style={'margin-left': 20, 'vertical-align': 'middle', 'width': 200}),
                #         dcc.Dropdown(['rmse', 'crmse', 'bias', 'bias_pct', 'mae', 'mae_pct'],
                #                      multi=True,
                #                      placeholder="Select at least one metric to be calculated and plotted",
                #                      style={'vertical-align': 'middle', 'width': 500, 'color': 'black'})
                #     ], style={'display': 'flex', 'margin-top': 5, 'margin-bottom': 5}),
                #     html.Div(children=[
                #         html.H5('Output Directory:', style={'margin-left': 20, 'vertical-align': 'middle', 'width': 200}),
                #         dcc.Input(placeholder="Output Directory Path", id='output_dir',
                #                   style={'vertical-align': 'middle', 'width': 500}),
                #         # dcc.Input(type='file', style={'webkitdirectory': 'true'}),
                #         # < input type = "file", id = "filepicker" name = "fileList" webkitdirectory multiple / >
                #         # dcc.Upload(
                #         #     html.A(
                #         #         html.Img(src='data:image/gif;base64,{}'.format(open_icon.decode()),
                #         #                  style={'vertical-align': 'middle', 'width': '25px', 'height': '25px'})),
                #         #     style={'margin-left': 10, 'vertical-align': 'middle'})
                #     ], style={'display': 'flex', 'margin-top': 5, 'margin-bottom': 5}),
                #     html.Div(children=[
                #         html.H5('Name of The Run:', style={'margin-left': 20, 'vertical-align': 'middle', 'width': 200}),
                #         dcc.Input(placeholder="name of the run appended to the name of any saved files",
                #                   style={'vertical-align': 'middle', 'width': 500},
                #                   required=True)
                #     ], style={'display': 'flex', 'margin-top': 5, 'margin-bottom': 5}),
                #     html.Div(children=[
                #         html.H5('Baseline Data Set:', style={'margin-left': 20, 'vertical-align': 'middle'}),
                #         dataset_form,
                #     ], style={'margin-top': 45, 'margin-bottom': 5}),
                #     html.Div(id='comp-config',
                #              children=[
                #                  html.H5('Compare Data Set(s):', style={'margin-left': 20, 'vertical-align': 'middle'}),
                #                  dataset_form,
                #     ], style={'margin-top': 45, 'margin-bottom': 5})
                # ])
            ], open=True),
            html.Hr(style={'margin-top': 0}),
            html.Div(
                html.Button('Run WeValidate',
                            id='run-validate',
                            style={'vertical-align': 'top', 'margin-top': -12, 'font-size': 30, 'border-radius': 8}),
                style={'textAlign': 'center'}
            ),
            dbc.Row(
                children=[
                    dcc.Store(id='unique-timeseries'),
                    dcc.Store(id='metrics-dict'),
                    dcc.Tabs(children=[
                        dcc.Tab(label='Time Series', children=[
                            html.Div(style={'height': 76}),
                            dcc.Graph(id='time_series', style={'padding-top': 20, 'height': '65vh'})
                        ], style=tab_style, selected_style=tab_selected_style),
                        dcc.Tab(label='Histogram', children=[
                            dbc.Row([
                                dbc.Col(html.Label('Data:', style={'vertical-align': 'middle', 'horizontal-align': 'right', 'textAlign': 'right'}), width=1),
                                dbc.Col(dcc.Dropdown(multi=True, id='histogram-dropdown',
                                                     style={'vertical-align': 'middle', 'width': 600, 'color': 'black'}), width=5),
                                dbc.Col(html.Label('Month:'), width=1),
                                dbc.Col(dcc.Dropdown(id='histogram-month',
                                                     style={'vertical-align': 'middle', 'width': 600, 'color': 'black'}), width=5)
                            ], style={'padding': 20}),
                            # dbc.Col(html.Label('Metrics:'), width=1),
                            # dbc.Col(dcc.Dropdown(multi=True, id='histogram-dropdown',
                            #              style={'vertical-align': 'middle', 'width': 500, 'color': 'black'}), width=5),
                            # dcc.DatePickerRange(
                            #     id='histogram-date_range',
                            #     minimum_nights=28,
                            #     clearable=True,
                            #     with_portal=True,
                            # ),

                            dcc.Graph(
                                id='histogram', style={'height': '65vh'}
                            ),
                            # dcc.Graph(
                            #     id='histogram2'
                            # ),
                        ], style=tab_style, selected_style=tab_selected_style),
                        dcc.Tab(label='Scatter Plot', children=[
                            dbc.Row([
                                dbc.Col(html.Label('X:'), width=1),
                                dbc.Col(dcc.Dropdown(id='scatter-dropdown1',
                                                     style={'vertical-align': 'middle', 'width': 300, 'color': 'black'}), width=3),
                                dbc.Col(html.Label('Y:'), width=1),
                                dbc.Col(dcc.Dropdown(id='scatter-dropdown2',
                                                     style={'vertical-align': 'middle', 'width': 300, 'color': 'black'}), width=3),
                                dbc.Col(html.Label('Month:'), width=1),
                                dbc.Col(dcc.Dropdown(id='scatter-month',
                                                     style={'vertical-align': 'middle', 'width': 300, 'color': 'black'}), width=3),
                            ], style={'padding': 20}),
                            dcc.Graph(
                                id='scatter-plot', style={'height': '65vh'}
                            ),
                        ], style=tab_style, selected_style=tab_selected_style),
                        dcc.Tab(label='Monthly Metrics', children=[
                            dbc.Row([
                                dbc.Col(html.Label('Metrics:'), width=1),
                                dbc.Col(dcc.Dropdown(id='metrics-dropdown',
                                                     style={'vertical-align': 'middle', 'width': 300, 'color': 'black'}))
                            ], style={'padding': 20}),
                            dcc.Graph(
                                id='metrics-plot', style={'height': '65vh'}
                            ),
                        ], style=tab_style, selected_style=tab_selected_style),
                        dcc.Tab(label='CSV Files', children=[
                            html.Div(style={'height': 76}),
                            dbc.Col(dbc.Row(children=[
                                dbc.Row([
                                    dcc.Link(id='timeseries-link', href='', target='_top')
                                ], style={'padding-top': 20, 'padding-left': 20}),
                                dbc.Row([
                                    dcc.Link(id='metrics-link', href='', target='_top')
                                ], style={'padding-left': 20}),
                                dbc.Row([
                                    dcc.Link(id='annual-link', href='', target='_top')
                                ], style={'padding-left': 20}),
                                dbc.Row([
                                    dcc.Link(id='monthly-link', href='', target='_top')
                                ], style={'padding-left': 20}),
                                dbc.Row([
                                    dcc.Link(id='weekly-link', href='', target='_top')
                                ], style={'padding-left': 20}),
                                dbc.Row([
                                    dcc.Link(id='daily-link', href='', target='_top')
                                ], style={'padding-left': 20}),
                                dbc.Row([
                                    dcc.Link(id='hourly-link', href='', target='_top')
                                ], style={'padding-left': 20})
                            ], style={'height': '65vh'}
                            ), width={"size": 3})
                        ], style=tab_style, selected_style=tab_selected_style),
                    ], style=tab_style,
                        # colors={
                        # "border": "WhiteSmoke",
                        # "primary": "#222",
                        # "background": "#222"}
                    ),
                    html.Div(children=[
                        html.Button('Save Outputs',
                                    id='save-output',
                                    style={'vertical-align': 'top', 'margin-top': 20, 'font-size': 30, 'border-radius': 8}),
                        dcc.Download(id="download")],
                        style={'textAlign': 'center'}
                    ),
                ],
                style={'height': '70vh', 'display': 'block'}, id='output'
            ),
            # html.Div(children=[
            #     dcc.Store(id='unique-timeseries'),
            #     dcc.Store(id='metrics-dict'),
            #     dcc.Tabs(children=[
            #         dcc.Tab(label='Time Series', children=dcc.Graph(id='time_series', style={'padding-top': 20}), style=tab_style, selected_style=tab_selected_style),
            #         dcc.Tab(label='Histogram', children=[
            #             dbc.Row([
            #                 dbc.Col(html.Label('Data:', style={'vertical-align': 'middle', 'horizontal-align': 'right', 'textAlign': 'right'}), width=1),
            #                 dbc.Col(dcc.Dropdown(multi=True, id='histogram-dropdown',
            #                                      style={'vertical-align': 'middle', 'width': 600, 'color': 'black'}), width=5),
            #                 dbc.Col(html.Label('Month:'), width=1),
            #                 dbc.Col(dcc.Dropdown(id='histogram-month',
            #                                      style={'vertical-align': 'middle', 'width': 600, 'color': 'black'}), width=5)
            #             ], style={'padding': 20}),
            #             # dbc.Col(html.Label('Metrics:'), width=1),
            #             # dbc.Col(dcc.Dropdown(multi=True, id='histogram-dropdown',
            #             #              style={'vertical-align': 'middle', 'width': 500, 'color': 'black'}), width=5),
            #             # dcc.DatePickerRange(
            #             #     id='histogram-date_range',
            #             #     minimum_nights=28,
            #             #     clearable=True,
            #             #     with_portal=True,
            #             # ),
            #
            #             dcc.Graph(
            #                 id='histogram'
            #             ),
            #             # dcc.Graph(
            #             #     id='histogram2'
            #             # ),
            #         ], style=tab_style, selected_style=tab_selected_style),
            #         dcc.Tab(label='Scatter Plot', children=[
            #             dbc.Row([
            #                 dbc.Col(html.Label('X:'), width=1),
            #                 dbc.Col(dcc.Dropdown(id='scatter-dropdown1',
            #                                      style={'vertical-align': 'middle', 'width': 300, 'color': 'black'}), width=3),
            #                 dbc.Col(html.Label('Y:'), width=1),
            #                 dbc.Col(dcc.Dropdown(id='scatter-dropdown2',
            #                                      style={'vertical-align': 'middle', 'width': 300, 'color': 'black'}), width=3),
            #                 dbc.Col(html.Label('Month:'), width=1),
            #                 dbc.Col(dcc.Dropdown(id='scatter-month',
            #                                      style={'vertical-align': 'middle', 'width': 300, 'color': 'black'}), width=3),
            #             ], style={'padding': 20}),
            #             dcc.Graph(
            #                 id='scatter-plot'
            #             ),
            #         ], style=tab_style, selected_style=tab_selected_style),
            #         dcc.Tab(label='Monthly Metrics', children=[
            #             dbc.Row([
            #                 dbc.Col(html.Label('Metrics:'), width=1),
            #                 dbc.Col(dcc.Dropdown(id='metrics-dropdown',
            #                                      style={'vertical-align': 'middle', 'width': 300, 'color': 'black'}))
            #             ], style={'padding': 20}),
            #             dcc.Graph(
            #                 id='metrics-plot'
            #             ),
            #         ], style=tab_style, selected_style=tab_selected_style),
            #         dcc.Tab(label='CSV Files', children=[
            #             dbc.Row([
            #                 dcc.Link('time series csv file', id='timeseries-link', href='')
            #             ], style={'padding-top': 20, 'padding-left': 20}),
            #             dbc.Row([
            #                 dcc.Link('metrics csv file', id='metrics-link', href='')
            #             ], style={'padding-left': 20}),
            #             dbc.Row([
            #                 dcc.Link('metrics annual csv file', id='annual-link', href='')
            #             ], style={'padding-left': 20}),
            #             dbc.Row([
            #                 dcc.Link('metrics monthly csv file', id='monthly-link', href='')
            #             ], style={'padding-left': 20}),
            #             dbc.Row([
            #                 dcc.Link('metrics weekly csv file', id='weekly-link', href='')
            #             ], style={'padding-left': 20}),
            #             dbc.Row([
            #                 dcc.Link('metrics daily csv file', id='daily-link', href='')
            #             ], style={'padding-left': 20}),
            #             dbc.Row([
            #                 dcc.Link('metrics hourly csv file', id='hourly-link', href='')
            #             ], style={'padding-left': 20})
            #         ], style=tab_style, selected_style=tab_selected_style),
            #     ], style=tab_style,
            #         # colors={
            #         # "border": "WhiteSmoke",
            #         # "primary": "#222",
            #         # "background": "#222"}
            #     ),
            #     html.Div(
            #         html.Button('Save Outputs',
            #                     id='save-output',
            #                     style={'vertical-align': 'top', 'margin-top': 20, 'font-size': 30, 'border-radius': 8}),
            #         style={'textAlign': 'center'}
            #     ),
            # ],
            #     id='output',
            #     style={'display': 'block'}
            # )
        ],
        fluid=True,
        style={"height": "100vh"},
    )

    app.run_server(debug=debug, port=port, dev_tools_props_check=False)


@app.callback(
    Output('configuration', 'data'),
    Output('start-time', 'value'),
    Output('end-time', 'value'),
    Output('metrics', 'value'),
    Output('output-dir', 'value'),
    Output('run-name', 'value'),
    Output('ref-var-name', 'value'),
    Output('ref-var-unit', 'value'),
    Output({"type": 'base', "parameter": "data-name", "index": 0}, 'value'),
    Output({"type": 'base', "parameter": "var-name", "index": 0}, 'value'),
    Output({"type": 'base', "parameter": "frequency", "index": 0}, 'value'),
    Output({"type": 'base', "parameter": "flag", "index": 0}, 'value'),
    # Output({"type": 'base', "parameter": "function", "index": 0}, 'value'),
    # Output({"type": 'comp', "parameter": "data-name", "index": 1}, 'value'),
    # Output({"type": 'comp', "parameter": "function", "index": 1}, 'value'),
    # Output({"type": 'comp', "parameter": "var-name", "index": 1}, 'value'),
    # Output({"type": 'comp', "parameter": "frequency", "index": 1}, 'value'),
    # Output({"type": 'comp', "parameter": "flag", "index": 1}, 'value'),
    # Output({"type": 'base', "parameter": "file-path", "index": 0}, 'value'),
    # Output({"type": ALL, "parameter": "data-name", "index": ALL}, 'value'),
    # Output({"type": ALL, "parameter": "function", "index": ALL}, 'value'),
    # Output({"type": ALL, "parameter": "var-name", "index": ALL}, 'value'),
    # Output({"type": ALL, "parameter": "frequency", "index": ALL}, 'value'),
    # Output({"type": ALL, "parameter": "flag", "index": ALL}, 'value'),
    # Output({"type": ALL, "parameter": "file-path", "index": ALL}, 'value'),
    # Output({"type": ALL, "parameter": "file-content", "index": ALL}, 'data'),
    Input('configuration-upload', 'contents'),
    State('configuration-upload', 'filename'),
    prevent_initial_call=True,)
def fill_config_from(content, filename):
    if content is not None:
        frags = filename.split('.')
        if len(frags) == 2 and frags[1] == 'yaml':
            content_type, content_string = content.split(',')
            decoded = base64.b64decode(content_string)
            conf = yaml.load(decoded, Loader=yaml.FullLoader)
            start = datetime.datetime.strftime(conf['time']['window']['start'], '%Y-%m-%dT%H:%M')
            end = datetime.datetime.strftime(conf['time']['window']['end'], '%Y-%m-%dT%H:%M')
            return conf, start, end, ','.join(conf['metrics']), conf['output']['path'], conf['output']['org'],\
                   conf['reference']['var'], conf['reference']['units'], conf['base']['name'],\
                   conf['base']['var'], conf['base']['freq'], conf['base']['flag'] # conf['base']['function'],
                   # conf['comp']['name'], conf['comp']['function'], conf['comp']['var'], conf['comp']['freq'],\
                   # conf['comp']['flag']
        else:
            return 'invalid config file'


@app.callback(
    Output('comp-config', 'children'),
    Input('add-data', 'n_clicks'),
)
def add_compare_dataset(click):
    patched_children = Patch()
    if click:
        patched_children.append(html.Hr(style={'margin-top': 5}))
    patched_children.append(_build_dataset_form('compare', click + 1))
    return patched_children
    # if click:
    #     children.append(html.Hr(style={'margin-top': 5}))
    #     children.append(_build_dataset_form())
    #     return children
    # else:
    #     raise PreventUpdate


@app.callback(
    Output({"type": MATCH, "parameter": "file-path", "index": MATCH}, 'value'),
    Output({"type": MATCH, "parameter": "file-content", "index": MATCH}, 'data'),
    Input({"type": MATCH, "parameter": "file-selection", "index": MATCH}, 'filename'),
    State({"type": MATCH, "parameter": "file-selection", "index": MATCH}, 'contents'),
    prevent_initial_call=True,
)
def select_file(filename_list, contents_list):
    if filename_list:
        content_dict = {}
        for filename, contents in zip(filename_list, contents_list):
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            df = pd.DataFrame()
            try:
                if 'csv' in filename:
                    # Assume that the user uploaded a CSV file
                    df = pd.read_csv(
                        io.StringIO(decoded.decode('utf-8')))
                elif 'xls' in filename:
                    # Assume that the user uploaded an excel file
                    df = pd.read_excel(io.BytesIO(decoded))
            except Exception as e:
                print(e)
                return html.Div([
                    'There was an error processing this file.'
                ])
            content_dict[filename] = df.to_dict()
        return ', '.join(filename_list), content_dict
    else:
        raise PreventUpdate


def _reorg_parameters(stime, etime, metrics, output_dir, run_name, ref_var, ref_unit, data_name, data_name_id, #function, function_id,
                var_name, var_name_id, frequency, frequency_id, flag, flag_id, input_files, input_files_id, input_df, input_df_id):
    conf = {'location': None, 'time': {}, 'metrics': [], 'output': {}, 'base': {}, 'comp': [], 'reference': {}}
    conf['time']['window'] = {}
    conf['time']['window']['start'] = datetime.datetime.strptime(stime, '%Y-%m-%dT%H:%M')
    conf['time']['window']['end'] = datetime.datetime.strptime(etime, '%Y-%m-%dT%H:%M')
    conf['metrics'] = metrics
    conf['output']['path'] = output_dir
    conf['output']['org'] = run_name
    conf['output']['save_metrics'] = True
    conf['output']['save_figs'] = True
    conf['output']['show_figs'] = True
    conf['output']['print_results'] = True
    conf['reference']['var'] = ref_var
    conf['reference']['units'] = ref_unit
    base_idx = [x['index'] for x in data_name_id if x['type'] == 'base'][0]
    conf['base']['name'] = data_name[base_idx]
    conf['base']['path'] = input_files[base_idx]
    # conf['base']['function'] = function[base_idx]
    conf['base']['function'] = 'csv'
    conf['base']['var'] = var_name[base_idx]
    conf['base']['freq'] = frequency[base_idx]
    conf['base']['flag'] = flag[base_idx]
    dfs = input_df[base_idx]
    df_dict = {}
    for key, v in dfs.items():
        # df = pd.DataFrame.from_dict(v, orient='index')
        df_dict[key] = pd.DataFrame.from_dict(v)
    conf['base']['df'] = df_dict
    comp_indices = [x['index'] for x in data_name_id if x['type'] == 'compare']
    for idx in comp_indices:
        comp = {}
        comp['name'] = data_name[idx]
        comp['path'] = input_files[idx]
        # comp['function'] = function[idx]
        comp['function'] = 'csv'
        comp['var'] = var_name[idx]
        comp['freq'] = frequency[idx]
        comp['flag'] = flag[idx]
        dfs = input_df[idx]
        df_dict = {}
        for key, v in dfs.items():
            df_dict[key] = pd.DataFrame.from_dict(v)
        comp['df'] = df_dict
        conf['comp'].append(comp)
    return conf


def _plot_timeseries(combined_df):
    # print(combined_df.columns)
    fig = go.Figure()
    lines = []
    df_unique = pd.DataFrame()
    for columnName, columnData in combined_df.items():
        # print('Column Name : ', columnName)
        # print('Column Contents : ', columnData.values)
        if columnName[1] not in lines:
            lines.append(columnName[1])
            fig.add_trace(go.Scatter(x=combined_df.index, y=columnData,
                                     mode='lines',
                                     name=columnName[1]))
            df_unique[columnName[1]] = columnData
    return fig, lines, df_unique


@app.callback(
    Output('output', 'style'),
    Output('time_series', 'figure'),
    Output('histogram-dropdown', 'options'),
    Output('unique-timeseries', 'data'),
    Output('histogram-dropdown', 'value'),
    Output('histogram-month', 'options'),
    # Output('histogram-date_range', 'start_date'),
    # Output('histogram-date_range', 'end_date'),
    # Output('histogram-date_range', 'min_date_allowed'),
    # Output('histogram-date_range', 'max_date_allowed'),
    Output('scatter-dropdown1', 'options'),
    Output('scatter-dropdown1', 'value'),
    Output('scatter-dropdown2', 'options'),
    Output('scatter-dropdown2', 'value'),
    Output('scatter-month', 'options'),
    Output('metrics-dropdown', 'options'),
    Output('metrics-dropdown', 'value'),
    Output('metrics-dict', 'data'),
    Output('timeseries-link', 'children'),
    Output('timeseries-link', 'href'),
    Output('metrics-link', 'children'),
    Output('metrics-link', 'href'),
    Output('annual-link', 'children'),
    Output('annual-link', 'href'),
    Output('monthly-link', 'children'),
    Output('monthly-link', 'href'),
    Output('weekly-link', 'children'),
    Output('weekly-link', 'href'),
    Output('daily-link', 'children'),
    Output('daily-link', 'href'),
    Output('hourly-link', 'children'),
    Output('hourly-link', 'href'),
    Input('run-validate', 'n_clicks'),
    Input('configuration-upload', 'contents'),
    State('configuration-upload', 'filename'),
    State('start-time', 'value'),
    State('end-time', 'value'),
    State('metrics', 'value'),
    State('output-dir', 'value'),
    State('run-name', 'value'),
    State('ref-var-name', 'value'),
    State('ref-var-unit', 'value'),
    State({"type": ALL, "parameter": "data-name", "index": ALL}, 'value'),
    State({"type": ALL, "parameter": "data-name", "index": ALL}, 'id'),
    # State({"type": ALL, "parameter": "function", "index": ALL}, 'value'),
    # State({"type": ALL, "parameter": "function", "index": ALL}, 'id'),
    State({"type": ALL, "parameter": "var-name", "index": ALL}, 'value'),
    State({"type": ALL, "parameter": "var-name", "index": ALL}, 'id'),
    State({"type": ALL, "parameter": "frequency", "index": ALL}, 'value'),
    State({"type": ALL, "parameter": "frequency", "index": ALL}, 'id'),
    State({"type": ALL, "parameter": "flag", "index": ALL}, 'value'),
    State({"type": ALL, "parameter": "flag", "index": ALL}, 'id'),
    State({"type": ALL, "parameter": "file-path", "index": ALL}, 'value'),
    State({"type": ALL, "parameter": "file-path", "index": ALL}, 'id'),
    State({"type": ALL, "parameter": "file-content", "index": ALL}, 'data'),
    State({"type": ALL, "parameter": "file-content", "index": ALL}, 'id'),
    # State('comp-config', 'children'),
    # State({"parameter": "file-path", "index": ALL}, 'value'),
    # State({"parameter": "file-path", "index": ALL}, 'id'),
    prevent_initial_call=True,
)
def run_validation(click, content, filename, stime, etime, metrics, output_dir, run_name, ref_var, ref_unit, data_name, data_name_id,
                   # function, function_id,
                   var_name, var_name_id, frequency, frequency_id, flag, flag_id,
                   input_files, input_files_id, input_df, input_df_id):
    triggered_id = ctx.triggered_id
    conf = {}
    if triggered_id == 'run-validate' and click:
    # if click:
        conf = _reorg_parameters(stime, etime, metrics, output_dir, run_name, ref_var, ref_unit, data_name, data_name_id,
                           # function, function_id,
                                 var_name, var_name_id, frequency, frequency_id, flag, flag_id,
                                 input_files, input_files_id, input_df, input_df_id)
        # combined_df, monthly_results = compare(conf)
        # time_series, histogram_options, unique_timeseries = _plot_timeseries(combined_df)
        # first_date = unique_timeseries.index[0]
        # last_date = unique_timeseries.index[-1]
        # year_month = list(set(unique_timeseries.index.to_period('M').astype(str).tolist()))
        # # year_month = ['All'] + list(set(year_month))
        # year_month.sort()
        # # _plot_metrics(monthly_results)
        # monthly_results.reset_index(inplace=True)
        # grouped = monthly_results.groupby(['compare'])
        # metrics_monthly_dict = {}
        # for item in grouped:
        #     item[1].reset_index(inplace=True, drop=True)
        #     for columnName, columnData in item[1].items():
        #         if columnName not in ['compare', 'base', 'index']:
        #             if columnName not in metrics_monthly_dict:
        #                 metrics_monthly_dict[columnName] = pd.DataFrame()
        #                 metrics_monthly_dict[columnName]['timestamp'] = pd.DataFrame(item[1]['index'])
        #             metrics_monthly_dict[columnName][item[0][0]] = columnData
        # metrics_monthly_dict2 = {}
        # for key, value in metrics_monthly_dict.items():
        #     metrics_monthly_dict2[key] = value.to_dict('records')
        # timeseries_link = 'time_series_' + run_name + '.csv'
        # metrics_link = 'metrics_' + run_name + '.csv'
        # annual_link = 'metrics_annual_' + run_name + '.csv'
        # monthly_link = 'metrics_monthly_' + run_name + '.csv'
        # weekly_link = 'metrics_weekly_' + run_name + '.csv'
        # daily_link = 'metrics_daily_' + run_name + '.csv'
        # hourly_link = 'metrics_hourly_' + run_name + '.csv'
        # return {'display': 'block'}, time_series, histogram_options, unique_timeseries.reset_index(names='index').to_dict('records'),\
        #        histogram_options, year_month, histogram_options, histogram_options[0],\
        #        histogram_options, histogram_options[-1], year_month, metrics, metrics[0], metrics_monthly_dict2, \
        #        timeseries_link, ('ms-excel:ofe|u|file:///' + output_dir + '/' + timeseries_link).replace('\\', '/'), \
        #        metrics_link, ('ms-excel:ofe|u|file:///' + output_dir + '/' + metrics_link).replace('\\', '/'), \
        #        annual_link, ('ms-excel:ofe|u|file:///' + output_dir + '/' + annual_link).replace('\\', '/'), \
        #        monthly_link, ('ms-excel:ofe|u|file:///' + output_dir + '/' + monthly_link).replace('\\', '/'), \
        #        weekly_link, ('ms-excel:ofe|u|file:///' + output_dir + '/' + weekly_link).replace('\\', '/'), \
        #        daily_link, ('ms-excel:ofe|u|file:///' + output_dir + '/' + daily_link).replace('\\', '/'), \
        #        hourly_link, ('ms-excel:ofe|u|file:///' + output_dir + '/' + hourly_link).replace('\\', '/')
        #         # first_date, last_date, first_date, last_date, \
    elif triggered_id == 'configuration-upload':
        if content is not None:
            frags = filename.split('.')
            if len(frags) == 2 and frags[1] == 'yaml':
                content_type, content_string = content.split(',')
                decoded = base64.b64decode(content_string)
                conf = yaml.load(decoded, Loader=yaml.FullLoader)
                # loads QC module
                # crosscheck_ts = eval_tools.get_module_class('qc', 'crosscheck_ts_csv')(conf)
                df = pd.read_csv(os.path.join((pathlib.Path(os.getcwd())), str(conf['base']['path'])))
                conf['base']['df'] = {conf['base']['path']: df}
                for comp in conf['comp']:
                    df = pd.read_csv(os.path.join((pathlib.Path(os.getcwd())), str(comp['path'])))
                    comp['df'] = {comp['path']: df}
    else:
        raise PreventUpdate
    combined_df, monthly_results = compare(conf)
    time_series, histogram_options, unique_timeseries = _plot_timeseries(combined_df)
    first_date = unique_timeseries.index[0]
    last_date = unique_timeseries.index[-1]
    year_month = list(set(unique_timeseries.index.to_period('M').astype(str).tolist()))
    # year_month = ['All'] + list(set(year_month))
    year_month.sort()
    # _plot_metrics(monthly_results)
    monthly_results.reset_index(inplace=True)
    grouped = monthly_results.groupby(['compare'])
    metrics_monthly_dict = {}
    for item in grouped:
        item[1].reset_index(inplace=True, drop=True)
        for columnName, columnData in item[1].items():
            if columnName not in ['compare', 'base', 'index']:
                if columnName not in metrics_monthly_dict:
                    metrics_monthly_dict[columnName] = pd.DataFrame()
                    metrics_monthly_dict[columnName]['timestamp'] = pd.DataFrame(item[1]['index'])
                metrics_monthly_dict[columnName][item[0][0]] = columnData
    metrics_monthly_dict2 = {}
    for key, value in metrics_monthly_dict.items():
        metrics_monthly_dict2[key] = value.to_dict('records')
    run_name = conf['output']['org']
    metrics = conf['metrics']
    output_dir = os.path.join((pathlib.Path(os.getcwd())), str(conf['output']['path']))
    timeseries_link = 'time_series_' + run_name + '.csv'
    metrics_link = 'metrics_' + run_name + '.csv'
    annual_link = 'metrics_annual_' + run_name + '.csv'
    monthly_link = 'metrics_monthly_' + run_name + '.csv'
    weekly_link = 'metrics_weekly_' + run_name + '.csv'
    daily_link = 'metrics_daily_' + run_name + '.csv'
    hourly_link = 'metrics_hourly_' + run_name + '.csv'
    return {'display': 'block'}, time_series, histogram_options, unique_timeseries.reset_index(names='index').to_dict('records'),\
           histogram_options, year_month, histogram_options, histogram_options[0],\
           histogram_options, histogram_options[-1], year_month, metrics, metrics[0], metrics_monthly_dict2, \
           timeseries_link, ('ms-excel:ofe|u|file:///' + output_dir + '/' + timeseries_link).replace('\\', '/'), \
           metrics_link, ('ms-excel:ofe|u|file:///' + output_dir + '/' + metrics_link).replace('\\', '/'), \
           annual_link, ('ms-excel:ofe|u|file:///' + output_dir + '/' + annual_link).replace('\\', '/'), \
           monthly_link, ('ms-excel:ofe|u|file:///' + output_dir + '/' + monthly_link).replace('\\', '/'), \
           weekly_link, ('ms-excel:ofe|u|file:///' + output_dir + '/' + weekly_link).replace('\\', '/'), \
           daily_link, ('ms-excel:ofe|u|file:///' + output_dir + '/' + daily_link).replace('\\', '/'), \
           hourly_link, ('ms-excel:ofe|u|file:///' + output_dir + '/' + hourly_link).replace('\\', '/')


@app.callback(
    Output('histogram', 'figure'),
    # Output('histogram2', 'figure'),
    Input('histogram-dropdown', 'value'),
    Input('histogram-month', 'value'),
    State('unique-timeseries', 'data'),
    State('ref-var-name', 'value'),
    State('ref-var-unit', 'value'),
    prevent_initial_call=True,
)
def draw_histogram(selected_series, selected_time, df_dict, ref_var, ref_unit):
    df = pd.DataFrame(df_dict)#.from_dict(df_dict)
    df['index'] = pd.to_datetime(df['index'])
    df.set_index('index', inplace=True)
    if selected_time:
        selected_time = datetime.datetime.strptime(selected_time, '%Y-%m')
        df = df[(df.index.month == selected_time.month) & (df.index.year == selected_time.year)]
    df2 = pd.melt(df[selected_series], value_name=ref_var, var_name='dataset')
    fig = go.Figure()
    for column in selected_series:
        fig.add_trace(go.Histogram(x=df.loc[:, column], nbinsx=20, name=column, autobinx=False))
    fig.update_layout(barmode='overlay', xaxis_title=ref_var + ' (' + ref_unit + ')')
    fig.update_traces(opacity=0.4)
    # fig.update_traces(opacity=0.4, xbins=dict(size=15))
    # fig = px.histogram(df.loc[:, selected_series], nbins=15, barmode="overlay", opacity=0.4)
    fig2 = px.histogram(df2, color='dataset', nbins=20, barmode="overlay", opacity=0.4)
    return fig#, fig2


@app.callback(
    Output('scatter-plot', 'figure'),
    Input('scatter-dropdown1', 'value'),
    Input('scatter-dropdown2', 'value'),
    Input('scatter-month', 'value'),
    State('unique-timeseries', 'data'),
    State('ref-var-name', 'value'),
    State('ref-var-unit', 'value'),
    prevent_initial_call=True,
)
def draw_scatterplot(x, y, selected_time, df_dict, ref_var, ref_unit):
    df = pd.DataFrame(df_dict)#.from_dict(df_dict)
    df['index'] = pd.to_datetime(df['index'])
    df.set_index('index', inplace=True)
    if selected_time:
        selected_time = datetime.datetime.strptime(selected_time, '%Y-%m')
        df = df[(df.index.month == selected_time.month) & (df.index.year == selected_time.year)]
    # df2 = pd.melt(df, value_name=ref_var, var_name='dataset')
    # fig = go.Figure()
    if x and y:
        fig = px.scatter(df, x=x, y=y, trendline="ols")
    else:
        fig = go.Figure()
    a = df.loc[:, x]
    b = [a.min(), a.max()]
    fig.add_trace(go.Scatter(x=b, y=b, name='1:1 line', mode='lines'))
    # # for column in selected_series:
    # #     fig.add_trace(go.Histogram(x=df.loc[:, column], nbinsx=20, name=column, autobinx=False))
    # fig.update_layout(barmode='overlay', xaxis_title=ref_var + ' (' + ref_unit + ')')
    # fig.update_traces(opacity=0.4)
    # # fig.update_traces(opacity=0.4, xbins=dict(size=15))
    # # fig = px.histogram(df.loc[:, selected_series], nbins=15, barmode="overlay", opacity=0.4)
    # fig2 = px.histogram(df2, color='dataset', nbins=20, barmode="overlay", opacity=0.4)
    return fig


@app.callback(
    Output('metrics-plot', 'figure'),
    Input('metrics-dropdown', 'value'),
    State('metrics-dict', 'data'),
    prevent_initial_call=True,
)
def draw_metricsplot(selected_metrics, metrics_dict):
    # df = pd.DataFrame(df_dict)#.from_dict(df_dict)
    # df['index'] = pd.to_datetime(df['index'])
    # df.set_index('index', inplace=True)
    # if selected_time:
    #     selected_time = datetime.datetime.strptime(selected_time, '%Y-%m')
    #     df = df[(df.index.month == selected_time.month) & (df.index.year == selected_time.year)]
    # # df2 = pd.melt(df, value_name=ref_var, var_name='dataset')
    # fig = go.Figure()
    if selected_metrics:
        df = pd.DataFrame(metrics_dict[selected_metrics]).set_index('timestamp')#.from_dict(df_dict)
        # df.set_index('timestamp')
        fig = px.line(df, x=df.index, y=df.columns)
        return fig
    else:
        return go.Figure()

    # if x and y:
    #     fig = px.scatter(df, x=x, y=y, trendline="ols")
    # else:
    #     fig = go.Figure()
    # a = df.loc[:, x]
    # b = [a.min(), a.max()]
    # fig.add_trace(go.Scatter(x=b, y=b, name='1:1 line', mode='lines'))
    # # # for column in selected_series:
    # # #     fig.add_trace(go.Histogram(x=df.loc[:, column], nbinsx=20, name=column, autobinx=False))
    # # fig.update_layout(barmode='overlay', xaxis_title=ref_var + ' (' + ref_unit + ')')
    # # fig.update_traces(opacity=0.4)
    # # # fig.update_traces(opacity=0.4, xbins=dict(size=15))
    # # # fig = px.histogram(df.loc[:, selected_series], nbins=15, barmode="overlay", opacity=0.4)
    # # fig2 = px.histogram(df2, color='dataset', nbins=20, barmode="overlay", opacity=0.4)
    return fig


@app.callback(
    Output("download", "data"),
    Input('save-output', 'n_clicks'),
    # State('time_series', 'figure'),
    # State('histogram', 'figure'),
    State('histogram-dropdown', 'options'),
    State('histogram-month', 'options'),
    State('unique-timeseries', 'data'),
    State('ref-var-name', 'value'),
    State('ref-var-unit', 'value'),
    # State('scatter-plot', 'figure'),
    # State('scatter-dropdown1', 'options'),
    # State('scatter-dropdown2', 'options'),
    # State('scatter-month', 'options'),
    # State('metrics-plot', 'figure'),
    State('metrics-dropdown', 'options'),
    State('metrics-dict', 'data'),
    State('output-dir', 'value'),
    State('run-name', 'value'),
    prevent_initial_call=True,
)
def save_output(click, datasets, months, timeseries_dict, ref_var, ref_unit, metrics, metrics_dict, output_dir, run_name):
    df = pd.DataFrame(timeseries_dict)
    df['index'] = pd.to_datetime(df['index'])
    df.set_index('index', inplace=True)
    fig = go.Figure()
    for columnName, columnData in df.items():
        fig.add_trace(go.Scatter(x=df.index, y=columnData,
                                 mode='lines',
                                 name=columnName))
    filename = output_dir + '/' + 'time_series_' + run_name + '.png'
    try:
        os.remove(filename)
    except OSError:
        pass
    fig.write_image(filename)

    # if selected_time:
    #     selected_time = datetime.datetime.strptime(selected_time, '%Y-%m')
    #     df = df[(df.index.month == selected_time.month) & (df.index.year == selected_time.year)]
    # df2 = pd.melt(df[selected_series], value_name=ref_var, var_name='dataset')
    fig = go.Figure()
    for column in datasets:
        fig.add_trace(go.Histogram(x=df.loc[:, column], nbinsx=20, name=column, autobinx=False))
    fig.update_layout(barmode='overlay', xaxis_title=ref_var + ' (' + ref_unit + ')')
    fig.update_traces(opacity=0.4)
    filename = output_dir + '/' + 'histogram_' + run_name + '.png'
    try:
        os.remove(filename)
    except OSError:
        pass
    fig.write_image(filename)
    # fig2 = px.histogram(df2, color='dataset', nbins=20, barmode="overlay", opacity=0.4)
    for x in range(len(datasets)):
        for y in range(x + 1, len(datasets)):
            fig = px.scatter(df, x=datasets[x], y=datasets[y], trendline="ols")
            a = df.loc[:, datasets[x]]
            b = [a.min(), a.max()]
            fig.add_trace(go.Scatter(x=b, y=b, name='1:1 line', mode='lines'))
            filename = output_dir + '/' + 'scatterplot_' + datasets[x] + '_vs_' + datasets[y] + '_' + run_name + '.png'
            try:
                os.remove(filename)
            except OSError:
                pass
            fig.write_image(filename)
    for month in months:
        selected_time = datetime.datetime.strptime(month, '%Y-%m')
        df_month = df[(df.index.month == selected_time.month) & (df.index.year == selected_time.year)]
        fig = go.Figure()
        for columnName, columnData in df_month.items():
            fig.add_trace(go.Scatter(x=df_month.index, y=columnData,
                                     mode='lines',
                                     name=columnName))
        filename = output_dir + '/' + 'time_series_' + month + '_' + run_name + '.png'
        try:
            os.remove(filename)
        except OSError:
            pass
        fig.write_image(filename)

        # if selected_time:
        #     selected_time = datetime.datetime.strptime(selected_time, '%Y-%m')
        #     df = df[(df.index.month == selected_time.month) & (df.index.year == selected_time.year)]
        # df2 = pd.melt(df[selected_series], value_name=ref_var, var_name='dataset')
        fig = go.Figure()
        for column in datasets:
            fig.add_trace(go.Histogram(x=df_month.loc[:, column], nbinsx=20, name=column, autobinx=False))
        fig.update_layout(barmode='overlay', xaxis_title=ref_var + ' (' + ref_unit + ')')
        fig.update_traces(opacity=0.4)
        filename = output_dir + '/' + 'histogram_' + month + '_' + run_name + '.png'
        try:
            os.remove(filename)
        except OSError:
            pass
        fig.write_image(filename)
        # fig2 = px.histogram(df2, color='dataset', nbins=20, barmode="overlay", opacity=0.4)
        for x in range(len(datasets)):
            for y in range(x + 1, len(datasets)):
                fig = px.scatter(df_month, x=datasets[x], y=datasets[y], trendline="ols")
                a = df_month.loc[:, datasets[x]]
                b = [a.min(), a.max()]
                fig.add_trace(go.Scatter(x=b, y=b, name='1:1 line', mode='lines'))
                filename = output_dir + '/' + 'scatterplot_' + month + '_' + datasets[x] + '_vs_' + datasets[y] + '_' + run_name + '.png'
                try:
                    os.remove(filename)
                except OSError:
                    pass
                fig.write_image(filename)
    for metric in metrics:
        df = pd.DataFrame(metrics_dict[metric]).set_index('timestamp')#.from_dict(df_dict)
        fig = px.line(df, x=df.index, y=df.columns)
        filename = output_dir + '/' + metric + '_monthly_' + run_name + '.png'
        try:
            os.remove(filename)
        except OSError:
            pass
        fig.write_image(filename)

    return dash.no_update


if __name__ == '__main__':
    _run_gui(debug=True, port=8088)
