# main components for callbacks
from dash import ALL, MATCH
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash import callback_context, no_update

# for the filtering
import pandas as pd
import numpy as np
import json
import time
from pprint import pprint

# for graphing
import plotly.express as px

# personal functions
from .graph_paramters import *
from .callback_header import *

# key words
DATA_VIEW = "data_views"
DISPLAY_INFO = "display_info"
UNIVERSITY = "university"
NONE = "None"

GAMSAT = 'gamsat'
GPA = 'gpa'
SUCCESS = 'success'

# the name for filter values
OFFER_PLACE_FILTER = 'offer uni place type'
PLACES_SELECTED_INCLUDE = 'places selected (include all)'
PLACES_SELECTED_EXCLUDE = 'places selected (exclude all)'
PLACES_SELECTED_NAME = 'places selected'
ALL_UNIQUE_FILTERS = [OFFER_PLACE_FILTER, PLACES_SELECTED_INCLUDE, PLACES_SELECTED_EXCLUDE]


# ------------------------------ FILTERING LOWER LEVEL --------------------------------------


# will convert a values object, and can all str instances of 'None' to np.nan
def convert_values_for_na(object):
    if (isinstance(object, str) and object == NONE):
        return np.nan
    elif (isinstance(object, list)):
        return [convert_values_for_na(item) for item in object]
    else:
        # keep the same
        return object


def condition_all(list_value, filter_value, exclude=False):
    # create an error for a value that isn't a list or na
    if (not isinstance(list_value, list) and pd.notna(list_value)):
        raise ValueError(list_value)
    
    # this case it must be na
    elif(not isinstance(list_value, list)):
        return True

    # handle the list value
    if (not exclude):
        # check that nothing new has been added (all included)
        return set(list_value) | set(filter_value) == set(list_value)
    else:
        # that nothing is in the intersection (exclude all)
        return set(list_value) & set(filter_value) == set()


# this is a really good function, exactly what I want
# - will filter the dataset based on the filter names and values
# - useful as doesn't require it to be in the interivew / offer format
def filter_dataset(uni_dataset, filter_names, filter_values): 
    filtered_dataset = uni_dataset.copy()

    # for each argument
    for filter_name, filter_value in zip(filter_names, filter_values):
        # skip uni filter as already dealt with
        if (filter_name == UNIVERSITY):
            continue

        # check for na so check
        converted_filter_value = convert_values_for_na(filter_value)

        # test to see if it is a multi select and create mask accordingly``
        if (not isinstance(filter_value, list)):
            curr_mask = filtered_dataset[filter_name] == converted_filter_value
        elif (not filter_name in ALL_UNIQUE_FILTERS):
            curr_mask = filtered_dataset[filter_name].isin(converted_filter_value)
        elif (filter_name == OFFER_PLACE_FILTER):
            # basically include all including na
            curr_mask = (filtered_dataset[filter_name].isin(converted_filter_value)) | \
                        (filtered_dataset[SUCCESS] == 'No')
        elif (filter_name == PLACES_SELECTED_INCLUDE):
            # basically check whether all of converted_filter_value are in x (nothing new added)
            curr_mask = (
                (filtered_dataset[PLACES_SELECTED_NAME].apply(
                lambda x: condition_all(x, converted_filter_value, exclude=False)
                )) & (filtered_dataset[SUCCESS] == 'No')
            ) | (
                (filtered_dataset[SUCCESS] == 'Yes')
            )
        elif (filter_name == PLACES_SELECTED_EXCLUDE):
            # basically check to see there is not intersection between the elements
            curr_mask = (
                (filtered_dataset[PLACES_SELECTED_NAME].apply(
                lambda x: condition_all(x, converted_filter_value, exclude=True)
                )) & (filtered_dataset[SUCCESS] == 'No')
            ) | (
                (filtered_dataset[SUCCESS] == 'Yes')
            )

        # filter using the mask
        filtered_dataset = filtered_dataset[curr_mask]

    return filtered_dataset


# ------------------------------ FILTERING HIGHER LEVEL --------------------------------------

# used to filter the data frame including with the university option
# - should include the data dictionary
def get_filtered_dataset(filter_settings, data_dictionaries):
    # get the filter names and values (includes university). Returns
    # 2. list of filter names
    # 3. list of corresponding filter values
    def get_settings_info(filter_settings, additional=True):
        # get data type
        data_type = filter_settings['data type']

        # start with the static filters
        filter_names = list(filter_settings[data_type]['static value'].keys())
        filter_values = list(filter_settings[data_type]['static value'].values())

        if (not additional):
            return filter_names, filter_values
        else:
            for active_filter in filter_settings[data_type]['active']:
                filter_names.append(active_filter)
                filter_values.append(filter_settings[data_type]['additional value'][active_filter])

            return filter_names, filter_values

    # get values from the settings
    data_type = filter_settings['data type']
    add_additional = filter_settings['additional filters']

    # get the unfiltered unviersity dataset
    selected_university = filter_settings[data_type]['static value'][UNIVERSITY]
    uni_dataset = data_dictionaries[DATA_VIEW][data_type][selected_university]

    # get the filter names for static values
    filter_names, filter_values = get_settings_info(filter_settings, additional=add_additional)
    filtered_dataset = filter_dataset(uni_dataset, filter_names, filter_values)
    
    return filtered_dataset


# ------------------------------ GRAPH --------------------------------------


# graph the dataframe with all the given options. Should include
# - adjusting the heading as well (TO DO)
def graph_dataframe(dataframe):
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
    

# ------------------------------ DATASETS --------------------------------------


def dataframe_to_data(dataframe, data_type):
    # convert the other data type to a string for readability
    if (data_type == 'offer'):
        dataframe['places selected'] = dataframe['places selected'].apply(
            lambda x: ", ".join(x) if isinstance(x, list) else x
        )

    return dataframe.to_json(orient="records")


# ------------------------------ CALLBACKS --------------------------------------


def register_change_graph_data(app, data_dictionaries):
    @app.callback(
        Output('graph-frame', 'data'),
        Input('filter-settings', 'data')
    )
    def change_graph_data(filter_settings_json):
        print("triggering change graph data")

        # load the data
        filter_settings = json.loads(filter_settings_json)

        # check if need to update
        if (set(filter_settings['actions']) & set([GRAPH_DATA_ACTION]) == set()):
            print("no update")
            raise PreventUpdate
        else:
            print("updating")

        # get the dataset settings
        data_type = filter_settings['data type']
        selected_university = filter_settings[data_type]['static value'][UNIVERSITY]
        
        # get the new dataset then
        uni_dataset = data_dictionaries[DATA_VIEW][data_type][selected_university]

        # save the data
        saved_dataset = dataframe_to_data(uni_dataset, data_type)

        return saved_dataset


def register_change_graph(app, data_dictionaries):
    # function will use the data dictionary to filter the options
    @app.callback(
        Output('scatter-plot-simple', 'figure'),
        Input('filter-settings', 'data')     # get the dataset type
    )
    def change_graph(filter_settings_json):
        # load the data
        filter_settings = json.loads(filter_settings_json)

        # check if need to update
        if (set(filter_settings['actions']) & set([GRAPH_ACTION]) == set()):
            raise PreventUpdate

        # use a filtering function
        filtered_frame = get_filtered_dataset(filter_settings, data_dictionaries)

        # graph the dataframe
        fig = graph_dataframe(filtered_frame)

        return fig


def register_click_data(app, data_dictionaries):
    @app.callback(
        Output('graph-info', 'columns'),
        Output('graph-info', 'data'),
        Input('scatter-plot-simple', 'selectedData'),
        State('graph-frame', 'data'),
        State('type-dropdown', 'value'),
        prevent_initial_call=True
    )
    def click_data_change(selected_data, filtered_frame_json, data_type):
        # don't update if nothing selected
        if (selected_data is None):
            return [], []

        # load the dataframe
        filtered_frame = pd.DataFrame(json.loads(filtered_frame_json))
        filtered_frame = filtered_frame.set_index('index')

        # find selected points and filter
        point_indices = [point['customdata'][0] for point in selected_data['points']]
        selected_df = filtered_frame.loc[point_indices]

        # get the current display columns
        display_columns = data_dictionaries[DISPLAY_INFO][data_type]
        display_column_names = [{"name": col, "id": col} for col in display_columns]

        # return the json
        return display_column_names, selected_df[display_columns].to_dict('records')


def register_callbacks(app, data_dictionaries):
    register_change_graph(app, data_dictionaries)
    register_click_data(app, data_dictionaries)
    register_change_graph_data(app, data_dictionaries)