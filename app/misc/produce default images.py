# core components for container
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

# importing
import pandas as pd
import ast

# for running the sever
import signal
import os

# create the app
app = Dash(
    __name__, 
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP],
    suppress_callback_exceptions=True
)

app.layout = html.Div([
    # get the style component
    html.Div(style={"height": "30vh"}),

    # get more stuff
    html.Div(
        [
            dbc.Stack(
                [
                    html.Div("Click "),
                    dbc.Button(
                        "save"
                    ),
                    html.Div(" to save images to carousel")
                ],
                direction="horizontal",
                gap=2,
                style={'justifyContent': 'center'}
            ),
        ],
        style={'justifyContent': 'center'}
    )
])

app.run_server(debug=True, port=8050, threaded=True)

