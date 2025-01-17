# --------------------------- MODULES --------------------------------------

# core components for container
from dash import Dash
import dash_bootstrap_components as dbc

# importing
import pandas as pd
import ast

# for running the sever
import signal
import os

# my own modules
from pages import page_layout
from pages import page_callbacks
import data

RELATIVE_IN = "../3. curated"

# ------------------------ EXECUTION --------------------------------------------

# intialize the datasets
interview_df = pd.read_csv(f"{RELATIVE_IN}/interview.csv", dtype=data.parameters.SCHEMA['interview'])
offer_df = pd.read_csv(f"{RELATIVE_IN}/offer.csv", dtype=data.parameters.SCHEMA['offer'])
offer_df['places selected'] = offer_df['places selected'].apply(lambda x: ast.literal_eval(x) if pd.notna(x) else x)
interview_df.columns, offer_df.columns = ['index'] + list(interview_df.columns)[1:], ['index'] + list(offer_df.columns)[1:]


# initalize the data functions
# - `filter_to_options`:    options of each filter
# - `filter_types`:         static/dynamic filters for each datasets
# - `data_views`:           the data views for each dataset and uni option
data_dictionaries = {
    # dictionaries to determine the types of data
    "filter_to_options": data.options.create_filter_to_options(interview_df, offer_df), 
    "filter_types": data.parameters.FILTER_TYPES,
    "display_info": data.parameters.DISPLAY_INFO,                          

    # precomputed views of the frame and the originals 
    "data_views": data.filtering.create_filters(interview_df, offer_df),
    'original_frames': {'interview': interview_df, 'offer': offer_df}
}

# create the app
app = Dash(
    __name__, 
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP],
    suppress_callback_exceptions=True
)

# create layout
app.layout = page_layout.create_layout(data_dictionaries)

# register callbacks
page_callbacks.register_callbacks(app, data_dictionaries)

# run app locally
try:
    app.run_server(debug=True, port=8050, threaded=True)
finally:
    os.kill(os.getpid(), signal.SIGTERM)
    print("Server stopped.")

