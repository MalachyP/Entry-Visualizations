from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc

# regular functions
import pandas as pd
import numpy as np
from collections import Counter

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
def get_y_range_histogram(percent_histograms):
    # get the max percentages for each trace
    max_percentages = [max(percent_histogram) * MAX_HEIGHT_EXPAND for percent_histogram in percent_histograms]

    # Set the y-axis limit dynamically (max of 60% or highest bin)
    y_max = max(BIN_HEIGHT, *max_percentages)

    return [0, y_max]


# gets the count histogram
def get_texts(count_histograms):
    texts = []
    for count_histogram in count_histograms:
        # discard values until non-zero reached
        start_idx = len(count_histogram)    # set as default value if nothing found
        for idx, count in enumerate(count_histogram):
            if (count != 0):
                start_idx = idx
                break

        # do the remaining values as text, replacing "0" with ""
        curr_text = [
            str(int(count)) if count else "" 
            for count in count_histogram
        ][start_idx:]

        # save the text
        texts.append(curr_text)

    return texts


# will
# - iterate through each legend option option in category order
# - create a corresponding dataframe
# - create a count histogram then a percent histogram
# returns
# - series views of COMBO, split on the legend
# - percent histogram
# - count histogram 
def get_histograms(dataframe, legend_option, category_order):
    # get the categories
    categories = category_order[legend_option]

    # find the maximum bin height
    bin_edges = np.arange(
        COMBO_BINS['start'], COMBO_BINS['end'] + COMBO_BINS['size'], COMBO_BINS['size']
    )

    # iterate through
    count_histograms = []   
    counts = np.zeros(len(categories))      # easy to sum
    for idx, legend_option_option in enumerate(categories):
        # get the current histogram
        curr_series = dataframe.loc[dataframe[legend_option] == legend_option_option, COMBO]
        curr_histogram = np.histogram(curr_series, bins=bin_edges)[0]

        # append information
        count_histograms.append(curr_histogram)
        counts[idx] = curr_histogram.sum()
    
    # get the histograms as percentages
    total_count = counts.sum()
    percent_histograms = [count_histogram / total_count * 100 for count_histogram in count_histograms]

    return percent_histograms, count_histograms


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


# can't do anything until I add the combo score unfortunately
def graph_histogram(dataframe, title, legend_option, data_type, data_dictionaries):
    # load in the settings
    category_order = data_dictionaries[LEGEND_GRADIENTS][data_type][legend_option][CATEGORY_ORDER]#[legend_option]
    legend_gradients = data_dictionaries[LEGEND_GRADIENTS][data_type][legend_option][COLOUR_DISCRETE_MAP]

    # include a percentage column to sum
    dataframe.loc[:, 'percentage'] = 100 / dataframe.shape[0]

    # get the histograms
    percent_histograms, count_histograms = get_histograms(dataframe, legend_option, category_order)

    fig = px.histogram(
        # main graphing
        dataframe,
        x=COMBO,
        y='percentage',
        histfunc='sum',
        color=legend_option,

        # get more formatting
        category_orders=category_order,
        color_discrete_map=legend_gradients
    )

    # get the text
    texts = get_texts(count_histograms)
    for i, trace in enumerate(fig.data):
        trace.update(
            text=texts[i],
            textposition='outside',
            texttemplate='%{text}'
        )
    
    # get more layout
    fig.update_layout(
        # titles and stuff
        title={
            "text": title,              # Title text
            "x": 0.5,                   # Center the title
            "xanchor": "center"         # Anchor text to the center
        },
        xaxis_title=COMBO,
        yaxis_title='Percentage',
        legend_title=SUCCESS,

        # axis range
        yaxis=dict(range=get_y_range_histogram(percent_histograms)),
        xaxis=dict(range=X_RANGE),

        # the histogram layout
        barmode='group',
        clickmode='event+select',
        bargap=0.2,

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