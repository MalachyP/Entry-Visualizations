import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px

import pandas as pd
import numpy as np

import signal
import os

app = dash.Dash(__name__)

app.layout = html.Div([
    "blah",
    dcc.Dropdown(
        id='drop',
        options=[
            'blah',
            'za'
        ],
        value='blah'
    ),
    html.Button("Add Input", id="add-input-button"),
    html.Div(id='dynamic-container'),  # Container for dynamic components
    html.Div(id='the one', children=[])     
])

@app.callback(
    Output('dynamic-container', 'children'),
    Input('add-input-button', 'n_clicks'),
    prevent_initial_call=True  # Prevents callback on initial load
)
def add_dynamic_input(n_clicks):
    if n_clicks is None:
        return None  # Return None if button hasn't been clicked
    return dcc.Input(id='alskdalfkj', type='text', value='default_value')

@app.callback(
    Output('the one', 'children'),
    Input('alskdalfkj', 'value'),
    Input('drop', 'value'),
    prevent_initial_call=True,
    suppress_callback_exceptions=True
)
def update(no_exist, option):
    if (no_exist is None):
        return option
    else:
        return "what???"

# run app locally
try:
    app.run_server(debug=True, port=8050, threaded=True)
finally:
    os.kill(os.getpid(), signal.SIGTERM)
    print("Server stopped.")