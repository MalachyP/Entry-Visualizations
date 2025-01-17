import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px

import pandas as pd
import numpy as np

import signal
import os

######################################################################################
################################ DATAFRAME FILTER ####################################
######################################################################################

RELATIVE_IN = "3. curated"

interview_df = pd.read_csv(f"{RELATIVE_IN}/interview.csv")
offer_df = pd.read_csv(f"{RELATIVE_IN}/offers.csv")

# get the unique unis
unique_unis = set(offer_df["offer uni"]) | set(offer_df["interview uni"])
unique_unis = [x for x in unique_unis if not pd.isna(x)]

def filter_uni_interview(df, uni_name):
    # Filter for rows where the university appears in interview or preferences columns
    df_filtered = df[
        (df['interview uni'] == uni_name) |
        (df['pref 1 uni'] == uni_name) |
        (df['pref 2 uni'] == uni_name) |
        (df['pref 3 uni'] == uni_name) |
        (df['pref 4 uni'] == uni_name) |
        (df['pref 5 uni'] == uni_name) |
        (df['pref 6 uni'] == uni_name)
    ].copy()
    
    # Define the success column
    df_filtered['success'] = np.where(df_filtered['interview uni'] == uni_name, 'Yes', 'No')
    
    # Calculate the preference number based on success
    df_filtered['preference'] = np.where(
        df_filtered['success'] == 'Yes',
        df_filtered[['pref 1 uni', 'pref 2 uni', 'pref 3 uni', 'pref 4 uni', 'pref 5 uni', 'pref 6 uni']].notna().sum(axis=1) + 1,
        np.select(
            [
                df_filtered['pref 1 uni'] == uni_name,
                df_filtered['pref 2 uni'] == uni_name,
                df_filtered['pref 3 uni'] == uni_name,
                df_filtered['pref 4 uni'] == uni_name,
                df_filtered['pref 5 uni'] == uni_name,
                df_filtered['pref 6 uni'] == uni_name
            ],
            [1, 2, 3, 4, 5, 6],
            default=np.nan
        )
    )
    
    # Select the appropriate gamsat and gpa based on where the uni appears
    df_filtered['gamsat'] = np.where(
        df_filtered['success'] == 'Yes',
        df_filtered['interview uni gamsat'],
        np.select(
            [
                df_filtered['pref 1 uni'] == uni_name,
                df_filtered['pref 2 uni'] == uni_name,
                df_filtered['pref 3 uni'] == uni_name,
                df_filtered['pref 4 uni'] == uni_name,
                df_filtered['pref 5 uni'] == uni_name,
                df_filtered['pref 6 uni'] == uni_name
            ],
            [
                df_filtered['pref 1 gamsat'],
                df_filtered['pref 2 gamsat'],
                df_filtered['pref 3 gamsat'],
                df_filtered['pref 4 gamsat'],
                df_filtered['pref 5 gamsat'],
                df_filtered['pref 6 gamsat']
            ],
            default=np.nan
        )
    )

    # Likewise for gpa
    df_filtered['gpa'] = np.where(
        df_filtered['success'] == 'Yes',
        df_filtered['interview uni gpa'],
        np.select(
            [
                df_filtered['pref 1 uni'] == uni_name,
                df_filtered['pref 2 uni'] == uni_name,
                df_filtered['pref 3 uni'] == uni_name,
                df_filtered['pref 4 uni'] == uni_name,
                df_filtered['pref 5 uni'] == uni_name,
                df_filtered['pref 6 uni'] == uni_name
            ],
            [
                df_filtered['pref 1 gpa'],
                df_filtered['pref 2 gpa'],
                df_filtered['pref 3 gpa'],
                df_filtered['pref 4 gpa'],
                df_filtered['pref 5 gpa'],
                df_filtered['pref 6 gpa']
            ],
            default=np.nan
        )
    )

    return df_filtered

def filter_uni_offer(df, uni_name):
    # Filter for rows where the university appears in either offer or interview columns
    df_filtered = df[
        (df['offer uni'] == uni_name) |
        (df['interview uni'] == uni_name)
    ].copy()
    
    # Define the success column based on whether the uni appears in the offer column
    df_filtered['success'] = np.where(df_filtered['offer uni'] == uni_name, 'Yes', 'No')
    
    # Define preference based on the year of preference for offer or interview uni preference
    df_filtered['preference'] = np.where(
        df_filtered['success'] == 'Yes',
        df_filtered['offer uni preference'],
        df_filtered['interview uni preference']
    )
    
    # Select the appropriate gamsat score based on where the uni appears (offer or interview)
    df_filtered['gamsat'] = np.where(
        df_filtered['success'] == 'Yes',
        df_filtered['offer uni gamsat'],
        df_filtered['interview uni gamsat']
    )

    # Select the appropriate gpa based on where the uni appears (offer or interview)
    df_filtered['gpa'] = np.where(
        df_filtered['success'] == 'Yes',
        df_filtered['offer uni gpa'],
        df_filtered['interview uni gpa']
    )

    # Define type: if 'offer uni place type' is not NaN, take its value; otherwise, take 'places selected'
    df_filtered['type'] = np.where(
        df_filtered['offer uni place type'].notna(),
        df_filtered['offer uni place type'],
        df_filtered['places selected']
    )

    return df_filtered

# Sample data for demonstration purposes
df = pd.DataFrame({
    'Year': [2020, 2021, 2022, 2020, 2021, 2022],
    'X Axis': [1, 2, 3, 4, 5, 6],
    'Y Axis': [7, 8, 9, 10, 11, 12],
    'Category': ['A', 'B', 'A', 'B', 'A', 'B']
})


######################################################################################
################################ GET THE APP #########################################
######################################################################################

# Initialize the app
app = dash.Dash(__name__)

X_VAR = "Gamsat"
Y_VAR = "GPA"

# Layout with filters
app.layout = html.Div([
    html.Div(
        html.H1('Investigation into medicine entry'),
        style={
            'display': 'flex',
            'justifyContent': 'center',
            'alignItems': 'center',
            'width': '100%'
        }
    ),

    # offers or interviews filter
    html.Div([
        dcc.Dropdown(
            id='stage-filter',
            options=[{'label': str(stage), 'value': stage} for stage in ["interviews", "offers"]],
            value="interviews",
            multi=False,
            placeholder="Select Stage"
        ),
        
    ], style={'width': '30%', 'display': 'inline-block'}),

    # Uni Filter
    html.Div([
        dcc.Dropdown(
            id='uni-filter',
            options=[{'label': str(uni_name), 'value': uni_name} for uni_name in unique_unis],
            value=unique_unis[0],
            multi=False,
            placeholder="Select University"
        )
    ], style={'width': '30%', 'display': 'inline-block'}),

    # Rural Filter
    html.Div([
        dcc.Dropdown(
            id='rural-filter',
            options=[{'label': str(rural_label), 'value': rural_label} for rural_label in ["Non-Rural", "Rural"]],
            value=["Non-Rural", "Rural"],
            multi=True,
            placeholder="Select Rurality"
        )
    ], style={'width': '30%', 'display': 'inline-block'}),

    # Year Filter
    html.Div([
        dcc.Dropdown(
            id='year-filter',
            options=[{'label': str(year), 'value': year} for year in [2022, 2023, 2024]],
            value=[2022, 2023, 2024],
            multi=True,
            placeholder="Select Year"
        )
    ], style={'width': '30%', 'display': 'inline-block'}),

    # Graph Output
    dcc.Graph(id='scatter-plot')
])

# Callback to update the plot based on filter selections
@app.callback(
    Output('scatter-plot', 'figure'),
    Input("stage-filter", 'value'),
    Input('uni-filter', 'value'),
    Input('year-filter', 'value'),
    Input('rural-filter', 'value')
)
def update_graph(stage, uni_name, selected_years, selected_ruralities):
    # select df
    if (stage == "interviews"):
        filtered_df = filter_uni_interview(interview_df, uni_name)
    else:
        filtered_df = filter_uni_offer(offer_df, uni_name)
    
    # Filter data based on selected years
    filtered_df = filtered_df[filtered_df['year'].isin(selected_years)]
    filtered_df = filtered_df[filtered_df['rurality'].isin(selected_ruralities)]

    # Create the plot based on selected variables for X and Y axes
    fig = px.scatter(
        filtered_df,
        x=X_VAR.lower(),
        y=Y_VAR.lower(),
        color='success',  # Coloring based on 'Category' for visualization
        title="GAMSAT vs GPA"
    )
    
    return fig

# run app locally
try:
    app.run_server(debug=True, port=8050, threaded=True)
finally:
    os.kill(os.getpid(), signal.SIGTERM)
    print("Server stopped.")

