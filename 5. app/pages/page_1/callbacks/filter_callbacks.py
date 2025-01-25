# main components for callbacks
from dash import ALL, MATCH, no_update
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash import callback_context

import ast
import json
from pprint import pprint

# personal functions
from ..layout.filter_layout import settings_to_additional_filters_layout, settings_to_filters, get_default_value
from ..layout import layout_parameters
from .callback_header import *

# names of dictionary data functions
FILTER_TO_OPTIONS = "filter_to_options"
FILTER_TYPES = "filter_types"

# Functions in this page
# 1. register_adjust_new_filters:    for when the user selects a new filter
# 2. register_delete_filter:         when the user decides to delete a filter
# 3. register_changing_environments: for changing the dataset being used

# to do
# 1. enable extra filters page


# ------------------------------ HELPER FUNCTIONS -------------------------------





##############################################################################
############################ REGISTERS  ######################################
##############################################################################


# ------------------------- Creation / deletion -----------------------------------------

# creates a new additional filter and reduces the options elsewhere
def register_adjust_new_filters(app):
    @app.callback(
        Output('filter-settings', 'data', allow_duplicate=True),
        Input('add-filter-dropdown', 'value'),                                  # input is the dropdown menu
        State('filter-settings', 'data'),                                       # get the current data
        prevent_initial_call=True,
        suppress_callback_exceptions=True
    )
    def adjust_data(new_filter, filter_settings_json):
        # Prevent unnecessary updates
        if not new_filter:
            raise PreventUpdate
        
        # read in the data
        filter_settings = json.loads(filter_settings_json)
        data_type = filter_settings['data type']

        # update the dictionary with the active filters
        filter_settings[data_type]['active'] = filter_settings[data_type]['active'] + [new_filter]

        # make sure additional filters changed only
        filter_settings['actions'] = [ADDITIONAL_ACTION]

        return json.dumps(filter_settings)


# delete the filter
def register_delete_filter(app, data_dictionaries):
    @app.callback(
        Output('filter-settings', 'data', allow_duplicate=True),                            # change the settings
        Input({'class': 'filters', 'filter': ALL, 'role': 'delete-button'}, 'n_clicks'),    # trigger is the delete button click
        State('filter-settings', 'data'),
        prevent_initial_call=True
    )
    def delete_filter(n_clicks, filter_settings_json):
        # check to see if the button has actually been clicked (note that all([]) is true)
        if (all([n_click is None for n_click in n_clicks])):
            raise PreventUpdate

        # read in the filter settings
        filter_settings = json.loads(filter_settings_json)
        data_type = filter_settings['data type']

        # figure out which filter is was
        ctx = callback_context
        triggered_id = ast.literal_eval(ctx.triggered[0]['prop_id'].split('.')[0])
        deleted_filter = triggered_id['filter']

        # update filter settings: remove deleted filter as an active filter
        filter_settings[data_type]['active'] = [active_filter for active_filter in filter_settings[data_type]['active']
                                                if active_filter != deleted_filter]     # remove from active filters
        
        # reset the filter options
        deleted_filter_options = data_dictionaries[FILTER_TO_OPTIONS][data_type][deleted_filter]
        deleted_filter_value = get_default_value(deleted_filter, deleted_filter_options)
        filter_settings[data_type]['additional value'][deleted_filter] = deleted_filter_value

        # make sure additional filters changed only
        filter_settings['actions'] = [ADDITIONAL_ACTION, GRAPH_ACTION]

        return json.dumps(filter_settings)


# -------------------------------- Additional stuff -------------------------


# toggling additional filters
def register_toggle_additional_filters(app):
    @app.callback(
        Output('filter-settings', 'data', allow_duplicate=True),
        Input('toggle-additional-filters', 'value'),
        State('filter-settings', 'data'),
        prevent_initial_call=True
    )
    def toggle_additional_filters(additional_filter_enablor, filter_settings_json):
        # read in the filter settings
        filter_settings = json.loads(filter_settings_json)

        # update the new toggle accordingly in settings
        filter_settings['additional filters'] = True if additional_filter_enablor != [] else False

        # make sure additional filters changed only
        filter_settings['actions'] = [ADDITIONAL_ACTION, GRAPH_ACTION]

        # return the filter layout
        return json.dumps(filter_settings)


# for changing settings each time a filter is changed
# Unforunately, it'll just have to trigger twice with the actual creation of a callback. 
# No issue I suppose as everything will still run co-currently (won't hamper anything)
# - I mean I guess this works if I'm taking the first callback context and it hasn't changed, because that 
#   means either a change in dataset happened or something, so need to change (notice ctx.triggered could be a list
#   but only taking the first value)
def register_alter_settings(app):
    @app.callback(
        Output('filter-settings', 'data', allow_duplicate=True),
        Input({'class': 'filters', 'filter': ALL, 'role': 'dropdown', 'type': ALL}, 'value'),
        State('filter-settings', 'data'),
        prevent_initial_call=True
    )
    def alter_settings(_, filter_settings_json):
        # read in the settings
        filter_settings = json.loads(filter_settings_json)
        data_type = filter_settings["data type"]

        # figure out which ID caused the trigger
        ctx = callback_context

        # check to see it's not triggered by a deletion
        if (ctx.triggered_id is None):
            raise PreventUpdate
        
        # get the filter that changed
        triggered_id = ast.literal_eval(ctx.triggered[0]['prop_id'].split('.')[0])
        triggered_filter_name = triggered_id['filter']

        # get the new value
        triggered_filter_value = ctx.triggered[0]['value']

        # update the dictionary (check if current filter in static value (same as keys))
        if (triggered_filter_name in filter_settings[data_type]['static value']):
            value_type = "static value"
        else:
            value_type = "additional value"
        
        # check to see if no update is needed
        if (filter_settings[data_type][value_type][triggered_filter_name] == triggered_filter_value):
            raise PreventUpdate
        
        # if not change the value
        filter_settings[data_type][value_type][triggered_filter_name] = triggered_filter_value

        # make sure it triggers the graph
        filter_settings['actions'] = [GRAPH_ACTION]

        # check if need to change the data
        if (triggered_filter_name == UNIVERSITY):
            filter_settings['actions'].append(GRAPH_DATA_ACTION)

        return json.dumps(filter_settings)


# ------------------------------- for changing the environment -------------------------------------


def register_change_dataset(app):
    @app.callback(
        Output('filter-settings', 'data', allow_duplicate=True),
        Input('type-dropdown', 'value'),
        State('filter-settings', 'data'),
        prevent_initial_call=True
    )
    def change_dataset(new_data_type, filter_settings_json):
        # load the data
        filter_settings = json.loads(filter_settings_json)

        # update the value
        filter_settings['data type'] = new_data_type

        # update the actions
        filter_settings['actions'] = [STATIC_ACTION, ADDITIONAL_ACTION, GRAPH_ACTION, GRAPH_DATA_ACTION]

        return json.dumps(filter_settings)


# ------------------------------- Actually creating the filters -----------------------------


# Note: this will even update for the graph callback as well
def register_settings_to_all_filters(app, data_dictionaries):
    @app.callback(
        Output('filter-static-container', 'children', allow_duplicate=True),
        Output('filter-additional-content', 'children', allow_duplicate=True),
        Input('filter-settings', 'data'),
        prevent_initial_call=True
    )
    def settings_to_all_filters(filter_settings_json):
        # load in the settings and determine the trigger
        filter_settings = json.loads(filter_settings_json)
        actions = filter_settings['actions']    # determine the actions to do

        # check if no update needed
        if (set(actions) & set([STATIC_ACTION, ADDITIONAL_ACTION]) == set()):
            raise PreventUpdate

        # deal with static content
        static_return = (
            settings_to_filters(filter_settings, data_dictionaries, static=True) 
            if (STATIC_ACTION in actions)
            else no_update
        )

        # deal with the additional content
        additional_return = (
            settings_to_additional_filters_layout(filter_settings, data_dictionaries) 
            if (ADDITIONAL_ACTION in actions)
            else no_update
        )

        # return all the info
        return static_return, additional_return


# ------------------------------- Final Step --------------------------------------

def register_callbacks(app, data_dictionaries):
    # for adding and removing filters
    register_adjust_new_filters(app)
    register_delete_filter(app, data_dictionaries)

    # other ways of updating settings
    register_toggle_additional_filters(app)
    register_alter_settings(app)

    # for actually creating changes
    register_settings_to_all_filters(app, data_dictionaries)

    # switching settings
    register_change_dataset(app)

