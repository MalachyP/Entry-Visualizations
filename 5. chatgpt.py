import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

import signal
import os

# Sample data for demonstration purposes
df = pd.DataFrame({
    'Year': [2020, 2021, 2022, 2020, 2021, 2022],
    'X Axis': [1, 2, 3, 4, 5, 6],
    'Y Axis': [7, 8, 9, 10, 11, 12],
    'Category': ['A', 'B', 'A', 'B', 'A', 'B']
})

# Initialize the app
app = dash.Dash(__name__)

# Layout with filters
app.layout = html.Div([
    html.Div(
        html.H1('blah'),
        style={
            'display': 'flex',
            'justifyContent': 'center',
            'alignItems': 'center',
            'width': '100%'
        }
    ),

    # Year Filter
    html.Div([
        dcc.Dropdown(
            id='year-filter',
            options=[{'label': str(year), 'value': year} for year in df['Year'].unique()],
            value=df['Year'].unique().tolist(),
            multi=True,
            placeholder="Select Year"
        )
    ], style={'width': '48%', 'display': 'inline-block'}),

    # X Axis Variable Filter
    html.Div([
        dcc.Dropdown(
            id='x-axis-filter',
            options=[{'label': 'X Axis', 'value': 'X Axis'}, {'label': 'Category', 'value': 'Category'}],
            value='X Axis',
            placeholder="Select X Axis Variable"
        )
    ], style={'width': '48%', 'display': 'inline-block'}),

    # Y Axis Variable Filter
    html.Div([
        dcc.Dropdown(
            id='y-axis-filter',
            options=[{'label': 'Y Axis', 'value': 'Y Axis'}, {'label': 'Category', 'value': 'Category'}],
            value='Y Axis',
            placeholder="Select Y Axis Variable"
        )
    ], style={'width': '48%', 'display': 'inline-block'}),

    # Graph Output
    dcc.Graph(id='scatter-plot')
])

# Callback to update the plot based on filter selections
@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('year-filter', 'value'),
     Input('x-axis-filter', 'value'),
     Input('y-axis-filter', 'value')]
)
def update_graph(selected_years, x_axis_var, y_axis_var):
    # Filter data based on selected years
    filtered_df = df[df['Year'].isin(selected_years)]

    # Create the plot based on selected variables for X and Y axes
    fig = px.scatter(
        filtered_df,
        x=x_axis_var,
        y=y_axis_var,
        color='Category',  # Coloring based on 'Category' for visualization
        title="Scatter Plot"
    )
    
    return fig

# run app locally
try:
    app.run_server(debug=True, port=8050)
finally:
    os.kill(os.getpid(), signal.SIGTERM)
    print("Server stopped.")

