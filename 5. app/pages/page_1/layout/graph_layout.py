from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc

# regular functions
import numpy as np

# for graphing
import plotly.express as px
import plotly.graph_objects as go

# my own functions
from .layout_parameters import *

# will make the width 8 when full page
HOVER_RESET = 'reset the graph'
HOVER_SAVE = 'save the graph to image carousel'
HOVER_DOWNLOAD = 'download image as jpg'

# create the default option
DEFAULT_LEGEND_OPTION = 'enter alternative legend' #'success'
DEFAULT_GRAPH_ID = 'graph'

# data dictionary key
LEGEND_OPTIONS = 'legend_options'
LEGEND_GRADIENTS = 'legend_gradients'
CATEGORY_ORDER = 'category order'
COLOUR_DISCRETE_MAP = 'color map discrete'

# Don't change (for axes)
GAMSAT = 'gamsat'
GPA = 'gpa'
SUCCESS = 'success'
COMBO = 'combo'


# ----------------------------- HELPER -------------------------------------------------------


# gets the bin height
def get_y_range_histogram(fig):
    # find the maximum bin height
    bin_edges = np.arange(
        COMBO_BINS['start'], 
        COMBO_BINS['end'] + COMBO_BINS['size'], 
        COMBO_BINS['size']
    )

    # Get histogram counts
    max_percentages = []
    for trace in fig.data:
        # get the percentages
        counts, _ = np.histogram(trace['x'], bins=bin_edges)

        # make sure to avoid no counts
        if (counts.sum() == 0):
            continue

        # get the percentages
        percentages = counts / counts.sum() * 100

        # make get the max percentage, and expand a touch
        max_percentages.append(percentages.max() * MAX_HEIGHT_EXPAND)

    # Set the y-axis limit dynamically (max of 60% or highest bin)
    y_max = max(BIN_HEIGHT, *max_percentages)

    return [0, y_max]


# gets the count histogram
def get_histograms(fig):
    # find the maximum bin height
    bin_edges = np.arange(
        COMBO_BINS['start'], 
        COMBO_BINS['end'] + COMBO_BINS['size'], 
        COMBO_BINS['size']
    )

    # get the count histogram for each trace
    histograms = [np.histogram(trace['x'], bins=bin_edges)[0] for trace in fig.data]

    return histograms


# ------------------------------ GRAPHING -----------------------------------------------------


# graph the dataframe with all the given options. Should include
# - adjusting the heading as well (TO DO)
def graph_scatter(dataframe, title, legend_option, data_type, data_dictionaries):
    #print(data_dictionaries[LEGEND_GRADIENTS][data_type][legend_option][CATEGORY_ORDER])
    #print(data_dictionaries[LEGEND_GRADIENTS][data_type][legend_option][COLOUR_DISCRETE_MAP])
    #print(list(dataframe[legend_option].unique()))

    # Create the plot based on selected variables for X and Y axes
    fig = px.scatter(
        # data input
        dataframe,
        x=GAMSAT,
        y=GPA,
        color=legend_option,
        custom_data='index',

        # formatting
        category_orders=data_dictionaries[LEGEND_GRADIENTS][data_type][legend_option][CATEGORY_ORDER],
        color_discrete_map=data_dictionaries[LEGEND_GRADIENTS][data_type][legend_option][COLOUR_DISCRETE_MAP],
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
            "text": title,  # Title text
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


# what I want
# - the combo scores of course, binned
# - 


# can't do anything until I add the combo score unfortunately
def graph_histogram(dataframe, title, legend_option, data_type, data_dictionaries):
    # create the figure
    fig = px.histogram(
        # data setting
        dataframe, 
        x=COMBO,
        color=SUCCESS,
#        custom_data=['index'],

        # histogram type
        histnorm='percent',
        barmode='group',

        # formatting
        text_auto=True
    )

    # get the histograms (will help for later)
    histograms = get_histograms(fig)

    # Manually set bin edges
    fig.update_traces(
        # bins
        xbins=COMBO_BINS,

        # text on the outside
        textfont_size=12, 
        textangle=0, 
        textposition="outside"#,
        #cliponaxis=False
    )

    # adding the text
    fig.update_layout(
        # tiltes and stuff
        title={
            "text": title,  # Title text
            "x": 0.5,                 # Center the title
            "xanchor": "center"       # Anchor text to the center
        },
        xaxis_title=COMBO,
        yaxis_title='Percentage',
        legend_title=SUCCESS
    )

    # customize layout further
    fig.update_layout(
        # the histogram layout
        bargap=0.2,

        # axis range
        yaxis=dict(range=get_y_range_histogram(fig)),
        xaxis=dict(range=X_RANGE),

        # whitespace
        margin=dict(l=20, r=20, t=40, b=20)  # Reduce whitespace (left, right, top, bottom)
    )
    

    return fig


# chooses which figure to create
def graph_dataframe(dataframe, filter_settings, data_dictionaries):
    # get the graph type
    graph_type = filter_settings['graph']['type']

    # get the default tile
    title = filter_settings['graph']['title']
    if (filter_settings['graph']['title'] is None):
        title = DEFAULT_TITLES[graph_type]

    # get the current legend options
    data_type = filter_settings['data type']
    legend_option = filter_settings[data_type]['legend']

    # check which kind of graph to create
    if (graph_type == 'scatter'):
        return graph_scatter(dataframe, title, legend_option, data_type, data_dictionaries)
    elif (graph_type == 'histogram'):
        return graph_histogram(dataframe, title, legend_option, data_type, data_dictionaries)
    else:
        return None


# ------------------------- COMPONENT FUNCTIONS -----------------------------------------------


# don't need a place-holder anymore, because doesn't make sense after first called
def create_legend_dropdown_component(filter_settings, data_dictionaries):
    # load in settings
    data_type = filter_settings['data type']
    legend_value = filter_settings[data_type]['legend']

    # get the legend options
    legend_options = data_dictionaries[LEGEND_OPTIONS][data_type]

    return dcc.Dropdown(
        options=legend_options,
        value=legend_value,  # start at success of course
        id={'class': 'graph', 'role': 'legend-dropdown'}
    )


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
                dcc.Graph(
                    id=graph_id,
                    config={
                        'doubleClick': False,
#                        'editable': True,
                        'modeBarButtonsToRemove': [
                            'toImage', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d'
                        ]
                    }
                ),

                # the stack for reset button, download button, save to image carousel
                html.Div(
                    [
                        # the legend option (in div to grow)
                        html.Div(
                            [
                                dbc.Input(
                                    placeholder="Enter graph title", 
                                    type="text",
                                    id={'class': 'graph', 'role': 'graph-title'}
                                )
                            ],
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
                            id={'class': 'graph', 'role': 'download-button'}
                        )
                    ],
                    className='d-flex gap-2 justify-content-end align-items-center',
                    style={'flex-wrap': 'nowrap'}
                ),

                html.Div(
                    [
                        html.Div(
                            dcc.Dropdown(
                                options=legend_options,
                                value=DEFAULT_LEGEND,  # start at success of course
                                placeholder=DEFAULT_LEGEND_OPTION,
                                id={'class': 'graph', 'role': 'legend-dropdown'}
                            ),
                            className='flex-grow-1',
                            id={'class': 'graph', 'role': 'legend-dropdown-container'}
                        ),

                        dbc.Switch(
                            label="histogram",
                            value=False,
                            id={'class': 'graph', 'role': 'graph-type-toggle'},
                            class_name="mt-2"
                        ),
                    ],
                    className='d-flex gap-2 justify-content-end align-items-start',
                    style={'flex-wrap': 'nowrap'}
                )

            ],
            gap=1
        ),
        width=width
    )


# ------------------------------- CREATING DEFAULT VALUES -------------------------------------


def create_default_graph(data_dictionaries):
    default_legend_options = data_dictionaries[LEGEND_OPTIONS]['interview']

    return [
        # create the single column
        create_graph_component(8, default_legend_options, graph_id=DEFAULT_GRAPH_ID)
    ]