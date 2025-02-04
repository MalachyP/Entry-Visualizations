# --------------------------- MODULES --------------------------------------

# core components for container
import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

# importing
import pandas as pd
import ast
from pprint import pprint

# for running the sever
import signal
import os

# my own modules
import data.dictionary
from pages import main_page, info_page
from pages import page_callbacks

RELATIVE_IN = "../3. curated"

# ------------------------ EXECUTION --------------------------------------------

# intialize the datasets
interview_df = pd.read_csv(
    f"{RELATIVE_IN}/interview.csv", 
    dtype=data.parameters.SCHEMA['interview'],
    na_values=[''],
    keep_default_na=False
)

# read in interview
offer_df = pd.read_csv(
    f"{RELATIVE_IN}/offer.csv", 
    dtype=data.parameters.SCHEMA['offer'],
    na_values=[''],
    keep_default_na=False
)

# read in the places properly
offer_df['places selected'] = offer_df['places selected'].apply(lambda x: ast.literal_eval(x) if pd.notna(x) else x)

# get the data dictionaries
data_dictionaries = data.dictionary.get_data_dictionaries(interview_df, offer_df)


# ------------------------ APP CREATION --------------------------------------------


# create the app
app = Dash(
    __name__, 
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP],
    suppress_callback_exceptions=True,
    use_pages=True
)

# register the pages
dash.register_page(
    "home", 
    path='/', 
    layout=main_page.page_layout.create_layout(data_dictionaries)
)

# register the pages
dash.register_page(
    "more information", 
    path='/more-information', 
    layout=info_page.page_layout.create_layout()
)

# create layout
app.layout = html.Div([
    dbc.Stack(
        [
            html.Div(
                dcc.Link(f"{page['name']}", href=page["relative_path"])
            ) for page in dash.page_registry.values()
        ],
        direction='horizontal',
        gap=2,
        className='top-bar'
    ),
    dash.page_container,
])

# register callbacks
page_callbacks.register_callbacks(app, data_dictionaries)

# run app locally
try:
    app.run_server(debug=True, port=8050, threaded=True)
finally:
    os.kill(os.getpid(), signal.SIGTERM)
    print("Server stopped.")

