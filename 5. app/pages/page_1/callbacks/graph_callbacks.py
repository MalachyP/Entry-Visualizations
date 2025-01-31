# main components for callbacks
from dash import dcc
from dash.dependencies import Input, Output, State
from dash import callback_context, no_update
from dash.exceptions import PreventUpdate

# for the filtering
import pandas as pd
import numpy as np
import json
from pprint import pprint

# for images
import io
import base64

import plotly.graph_objects as go

# personal functions
from .callback_header import *
from ..layout.graph_layout import graph_dataframe, create_legend_dropdown_component
from ..layout.layout_parameters import SUCCESS, DEFAULT_TITLES

# key words
DATA_VIEW = "data_views"
DISPLAY_INFO = "display_info"
UNIVERSITY = "university"
NONE = "None"

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


# ------------------------------ DATASETS --------------------------------------


def dataframe_to_data(dataframe, data_type):
    # convert the other data type to a string for readability
    if (data_type == 'offer'):
        dataframe['places selected'] = dataframe['places selected'].apply(
            lambda x: ", ".join(x) if isinstance(x, list) else x
        )

    return dataframe.to_json(orient="records")


# check how many triggers
def n_triggers():
    ctx = callback_context
    if not ctx.triggered:
        return 0  # No inputs triggered
    return len(ctx.triggered)


# ------------------------------- IMAGE CREATION -------------------------------


def create_image_src(figure_dict):
    # load in the figure
    figure = go.Figure(figure_dict)

    # get the image into the buffer
    buf = io.BytesIO()
    figure.write_image(buf, format="png")
    buf.seek(0)

    # get the new image and src
    new_image = base64.b64encode(buf.read()).decode("utf-8")
    new_src = f"data:image/png;base64,{new_image}"

    return new_src


# ------------------------------------------------------------------------------
# ------------------------------ CALLBACKS --------------------------------------
# -------------------------------------------------------------------------------


# ------------------------------ BUTTONS --------------------------------------


# switches between graph types
def register_toggle_graph_type(app):
    @app.callback(
        Output('filter-settings', 'data', allow_duplicate=True),
        Input({'class': 'graph', 'role': 'graph-type-toggle'}, 'value'),
        State('filter-settings', 'data'),
        prevent_initial_call=True
    )
    def toggle_graph_type(is_histogram, filter_settings_json):
        # load in the settings
        filter_settings = json.loads(filter_settings_json)

        # check which type to switch to
        if (is_histogram):
            filter_settings['graph']['type'] = 'histogram'
        else:
            filter_settings['graph']['type'] = 'scatter'
        
        # only need to change the graph not data
        filter_settings['actions'] = [GRAPH_ACTION, GRAPH_CLICK_DATA_ACTION]

        return json.dumps(filter_settings)


# reset
def register_reset_graph(app):
    @app.callback(
        Output('filter-settings', 'data'),
        Input({'class': 'graph', 'role': 'reset-button'}, 'n_clicks'),
        State('filter-settings', 'data'),
        prevent_initial_call=True
    )
    def reset_graph(n_clicks, filter_settings_json):
        # load in the settings
        filter_settings = json.loads(filter_settings_json)

        # make sure to reload the graph only
        filter_settings['actions'] = [GRAPH_ACTION, GRAPH_CLICK_DATA_ACTION]

        # return the default settings
        return json.dumps(filter_settings)


# download
def register_download_graph(app):
    @app.callback(
        Output('download', 'data', allow_duplicate=True),
        Input({'class': 'graph', 'role': 'download-button'}, 'n_clicks'),
        State('graph', 'figure'),
        prevent_initial_call=True
    )
    def download_graph(n_clicks, figure_dict):
        # load the image
        figure = go.Figure(figure_dict)

        # save the image
        img_bytes = figure.to_image(format="png")

        return dcc.send_bytes(img_bytes, "plot.png")


# will have two inputs where either one will work
def register_graph_title(app):
    @app.callback(
        Output('graph', 'figure', allow_duplicate=True),
        Output('filter-settings', 'data', allow_duplicate=True),
        Input({'class': 'graph', 'role': 'graph-title'}, 'n_blur'),     # is basically clicking away
        Input({'class': 'graph', 'role': 'graph-title'}, 'n_submit'),   # is basically pressing the enter button
        State({'class': 'graph', 'role': 'graph-title'}, 'value'),      # basically getting what's written
        State('graph', 'figure'),
        State({'class': 'graph', 'role': 'graph-type-toggle'}, 'value'),    # for deciding default title
        State('filter-settings', 'data'),                   # add filter settings for keeping the title
        prevent_initial_call=True
    )
    def change_graph_title(_a, _b, new_graph_title, figure_dict, is_histogram, filter_settings_json):
        # load in the settings
        filter_settings = json.loads(filter_settings_json)

        # decide what the new title would be
        if (not new_graph_title):
            graph_type = 'histogram' if is_histogram else 'scatter'
            new_graph_title = DEFAULT_TITLES[graph_type]

        # check if no update necessary
        if (filter_settings['graph']['title'] == new_graph_title):
            raise PreventUpdate

        # save the title
        filter_settings['graph']['title'] = new_graph_title

        # load the figure
        figure = go.Figure(figure_dict)

        # change the title
        figure.update_layout(
            title = {
                "text": new_graph_title,
                "x": 0.5,                 # Center the title
                "xanchor": "center"       # Anchor text to the center
            }
        )

        # no need to change the graph again
        filter_settings['actions'] = []

        return figure, json.dumps(filter_settings)


def register_add_image_carousel(app):
    @app.callback(
        Output('carousel-settings', 'data'),
        Input({'class': 'graph', 'role': 'save-image'}, 'n_clicks'),    # when the graph is initially saved
        State('graph', 'figure'),                                       # want to save the new graph
        State('carousel-settings', 'data'),                         # want to get the former children
        prevent_initial_call=True
    )
    def add_image_carousel(n_clicks, figure_dict, carousel_settings_json):
        # load in the data
        carousel_settings = json.loads(carousel_settings_json)

        # create a new image
        new_src = create_image_src(figure_dict)

        # get the new item
        new_key = len(carousel_settings['slide items']) + 1
        new_item = {"key": new_key, "src": new_src}

        # append to the list
        carousel_settings['slide items'].append(new_item)

        # make sure to change the action
        carousel_settings['actions'] = [CAROUSEL_ACTION]

        return json.dumps(carousel_settings)


def register_alter_settings_legend(app):
    @app.callback(
        Output('filter-settings', 'data', allow_duplicate=True),
        Input({'class': 'graph', 'role': 'legend-dropdown'}, 'value'),
        State('filter-settings', 'data'),
        prevent_initial_call=True
    )
    def alter_settings_legend(new_legend_value, filter_settings_json):
        # load settings
        filter_settings = json.loads(filter_settings_json)
        data_type = filter_settings['data type']

        # check to see if there is a change to make
        if (filter_settings[data_type]['legend'] == new_legend_value):
            raise PreventUpdate
        
        # change the settings and return
        filter_settings[data_type]['legend'] = new_legend_value

        # only need to graph
        filter_settings['actions'] = [GRAPH_ACTION]

        return json.dumps(filter_settings)


# ------------------------------ GRAPH DATA --------------------------------------


def register_click_data(app, data_dictionaries):
    @app.callback(
        Output('graph-info', 'columns', allow_duplicate=True),
        Output('graph-info', 'data', allow_duplicate=True),
        Output('graph', 'selectedData'),
        Input('graph', 'selectedData'),
        State('graph-frame', 'data'),
        State('type-dropdown', 'value'),
        prevent_initial_call=True
    )
    def click_data_change(selected_data, filtered_frame_json, data_type):
        # don't update if reset or at the start
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
        return display_column_names, selected_df[display_columns].to_dict('records'), None


# ------------------------------ FUNCTION CALLS -------------------------------------


def register_settings_to_graph(app, data_dictionaries):
    # function will use the data dictionary to filter the options
    @app.callback(
        Output('graph', 'figure'),
        Output('graph-info', 'columns'),
        Output('graph-info', 'data'),
        Output({'class': 'graph', 'role': 'legend-dropdown-container'}, 'children'),
        Output('graph-frame', 'data'),
        Input('filter-settings', 'data')     # get the dataset type
    )
    def settings_to_graph(filter_settings_json):
        # load the data
        filter_settings = json.loads(filter_settings_json)
        data_type = filter_settings['data type']
        actions = filter_settings['actions']

        # create the default values
        fig_return = column_return = data_return = legend_return = dataframe_return = no_update
        
        # FIGURE UPDATE
        if (GRAPH_ACTION in actions):
            # use a filtering function
            filtered_frame = get_filtered_dataset(filter_settings, data_dictionaries)

            # graph the dataframe
            fig_return = graph_dataframe(filtered_frame, filter_settings, data_dictionaries)

        # UPDATE FRAME
        if (GRAPH_DATA_ACTION in actions):
            dataframe_return = dataframe_to_data(filtered_frame, data_type)

        # CLICK DATA UPDATE
        if (GRAPH_CLICK_DATA_ACTION in actions):
            column_return, data_return = [], []
        
        # LEGEND UPDATE
        if (DATASET_CHANGE_ACTION in actions):
            legend_return = create_legend_dropdown_component(filter_settings, data_dictionaries)

        return fig_return, column_return, data_return, legend_return, dataframe_return


def register_callbacks(app, data_dictionaries):
    # button callbacks
    register_toggle_graph_type(app)
    register_reset_graph(app)
    register_download_graph(app)
    register_graph_title(app)
    register_add_image_carousel(app)
    register_alter_settings_legend(app)

    # more important callbacks
    register_settings_to_graph(app, data_dictionaries)
    register_click_data(app, data_dictionaries)