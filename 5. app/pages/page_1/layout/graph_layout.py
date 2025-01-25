from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc

# for graphing
import plotly.express as px

# my own functions
from .layout_parameters import *

# will make the width 8 when full page
HOVER_RESET = 'reset the graph'
HOVER_SAVE = 'save the graph to image carousel'
HOVER_DOWNLOAD = 'download image as jpg'

# create the default option
DEFAULT_LEGEND_OPTION = 'success'

# Don't change (for axes)
GAMSAT = 'gamsat'
GPA = 'gpa'
SUCCESS = 'success'


# ------------------------------ GRAPHING -----------------------------------------------------


# graph the dataframe with all the given options. Should include
# - adjusting the heading as well (TO DO)
def graph_scatter(dataframe):
    # Create the plot based on selected variables for X and Y axes
    fig = px.scatter(
        # data input
        dataframe,
        x=GAMSAT,
        y=GPA,
        color=SUCCESS,
        custom_data='index',

        # formatting
        category_orders=CATEGORY_ORDERS,
        color_discrete_map=COLOUR_DISCRETE_MAP,
        opacity=OPACITY,
    )

    # Fix axis limits
    fig.update_layout(
        xaxis=dict(range=GAMSAT_LIM),   # Set x-axis limits
        yaxis=dict(range=GPA_LIM),      # Set y-axis limits
        clickmode='event+select'
    ),

    # Customize layout
    fig.update_layout(
        title={
            "text": "GAMSAT vs GPA",  # Title text
            "x": 0.5,                 # Center the title
            "xanchor": "center"       # Anchor text to the center
        },
        margin=dict(l=20, r=20, t=40, b=20),  # Reduce whitespace (left, right, top, bottom)
    ),

    # Increase marker size by setting 'marker_size' in update_traces
    fig.update_traces(
        marker=dict(size=10)    # Adjust size as needed
    )  

    return fig


def graph_histogram(dataframe):
    # Create the plot based on selected variables for X and Y axes
    fig = px.histogram(
        # data input
        dataframe,
        x=GAMSAT,
        y=GPA,
        color=SUCCESS,
        custom_data='index',

        # formatting
        category_orders=CATEGORY_ORDERS,
        color_discrete_map=COLOUR_DISCRETE_MAP,
        opacity=OPACITY,
    )


# chooses which figure to create
def graph_dataframe(dataframe, filter_settings):
    # check which kind of graph to create
    if (filter_settings['graph type'] == 'scatter'):
        return graph_scatter(dataframe)
    elif (filter_settings['graph type'] == 'histogram'):
        return graph_histogram(dataframe)
    else:
        return None


# ------------------------- COMPONENT FUNCTIONS -----------------------------------------------

# will output a column containing a graph
# - graph_type: whether it's the simple or the advanced
# - width: how wide the graph element is (6 for 2 and 8 for 1 I believe)
# - options: the options for the custom legend
def create_graph_component(width, legend_options, graph_id=None):
    if (not graph_id):
        graph_id = {'class': 'graph', 'role': 'graph'}

    return dbc.Col(
        # the stack for the top bar, graph and legend type 
        dbc.Stack(
            [
                # the graph component
                dcc.Graph(id=graph_id),

                # the stack for reset button, download button, save to image carousel
                html.Div(
                    [
                        # the legend option (in div to grow)
                        html.Div(
                            dcc.Dropdown(
                                options=legend_options,
                                value=DEFAULT_LEGEND_OPTION,
                                placeholder=DEFAULT_LEGEND_OPTION,
                                id={'class': 'graph', 'role': 'legend-dropdown'}
                            ),
                            className='flex-grow-1'
                        ),

                        # reset basically
                        dbc.Button(
                            'reset',
                            title=HOVER_RESET,
                            id={'class': 'graph', 'role': 'reset-button'}
                        ),
                        dbc.Button(
                            'save',
                            title=HOVER_SAVE,
                            id={'class': 'graph', 'role': 'save-image'}
                        ),
                        dbc.Button(
                            html.I(className="bi bi-download"),
                            title=HOVER_DOWNLOAD,
                            id={'class': 'graph', 'role': 'download'}
                        )
                    ],
                    className='d-flex gap-2 justify-content-end align-items-center',
                    style={'flex-wrap': 'nowrap'}
                ),
            ],
            gap=1
        ),
        width=width
    )


# ------------------------------- CREATING DEFAULT VALUES -------------------------------------

def create_default_graph():
    return [
        # create the single column
        create_graph_component(8, ['Yes', 'No'], graph_id='graph')
    ]