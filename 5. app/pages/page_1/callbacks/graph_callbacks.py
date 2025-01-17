# main components for callbacks
from dash import ALL, MATCH
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash import callback_context

# for the filtering
import pandas as pd
import numpy as np

# for graphing
import plotly.express as px

# key words
DATA_VIEW = "data_views"
DISPLAY_INFO = "display_info"
UNIVERSITY = "university"
NONE = "None"

GAMSAT = 'gamsat'
GPA = 'gpa'
SUCCESS = 'success'

GAMSAT_LIM = [55, 85]
GPA_LIM = [5.2, 7.2]

# for the legend aspect
COLOUR_DISCRETE_MAP = {
    'Yes': 'blue',
    'No': 'red'
}
CATEGORY_ORDERS = {
    SUCCESS: ['Yes', 'No']
}
OPACITY = 0.7

# the name for filter values
OFFER_PLACE_FILTER = 'offer uni place type'
PLACES_SELECTED_INCLUDE = 'places selected (include all)'
PLACES_SELECTED_EXCLUDE = 'places selected (exclude all)'
PLACES_SELECTED_NAME = 'places selected'
ALL_UNIQUE_FILTERS = [OFFER_PLACE_FILTER, PLACES_SELECTED_INCLUDE, PLACES_SELECTED_EXCLUDE]


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


# used to filter the data frame including with the university option
# - should include the data dictionary
def filter_dataset(filter_values, filters_ids, data_type, data_dictionaries):
    # get the filter names
    filter_names = [filter_id['filter'] for filter_id in filters_ids]

    # get the selected university filter
    university_index = filter_names.index(UNIVERSITY)
    university_selected = filter_values[university_index]

    # get the unfiltered unviersity dataset
    filtered_dataset = data_dictionaries[DATA_VIEW][data_type][university_selected]

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
    

def register_change_graph(app, data_dictionaries):
    # function will use the data dictionary to filter the options
    @app.callback(
        Output('scatter-plot-simple', 'figure'),       # output the graph
        Output('graph-frame', 'data'),   # save the filtered frame
        Input({'class': 'filters', 'filter': ALL, 'role': 'dropdown', 'type': ALL}, 'value'),   # get the values
        State({'class': 'filters', 'filter': ALL, 'role': 'dropdown', 'type': ALL}, 'id'),      # get the ids
        State('type-dropdown', 'value')         # get the dataset type
    )
    def change_graph(filter_values, filters_ids, data_type):
        # use a filtering function
        filtered_frame = filter_dataset(filter_values, filters_ids, data_type, data_dictionaries)

        # convert the other data type to a string for readability
        if (data_type == 'offer'):
            filtered_frame['places selected'] = filtered_frame['places selected'].apply(
                lambda x: " ,".join(x) if isinstance(x, list) else x
            )

        # graph the dataframe
        fig = graph_dataframe(filtered_frame)

        return fig, filtered_frame.to_json(orient="records")

import json

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