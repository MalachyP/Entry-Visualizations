# main components for callbacks
from dash import ALL, no_update
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash import callback_context

import ast
import json

# personal functions
from ..layout.filter_layout import create_static_filter, create_additional_filter, \
                                   settings_to_additional_filters_layout, settings_to_filters

# names of dictionary data functions
FILTER_TO_OPTIONS = "filter_to_options"
FILTER_TYPES = "filter_types"

STATIC_ACTION = 'static'
ADDITIONAL_ACTION = 'additional'

# Functions in this page
# 1. register_adjust_new_filters:    for when the user selects a new filter
# 2. register_delete_filter:         when the user decides to delete a filter
# 3. register_changing_environments: for changing the dataset being used

# to do
# 1. enable extra filters page


##############################################################################
############################ REGISTERS  ######################################
##############################################################################


# creates a new additional filter and reduces the options elsewhere
def register_adjust_new_filters(app):
    @app.callback(
        Output('filter-settings', 'data'),
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
        deleted_filter = triggered_id["filter"]

        # update filter settings: remove deleted filter as an active filter
        filter_settings[data_type]['active'] = [active_filter for active_filter in filter_settings[data_type]['active']
                                                if active_filter != deleted_filter]     # remove from active filters
        
        # update filter settings: reset the filter options
        filter_settings[data_type]['additional value'][deleted_filter] = data_dictionaries[FILTER_TO_OPTIONS][data_type][deleted_filter]

        # make sure additional filters changed only
        filter_settings['actions'] = [ADDITIONAL_ACTION]

        return json.dumps(filter_settings)


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
        filter_settings['actions'] = [ADDITIONAL_ACTION]

        # return the filter layout
        return json.dumps(filter_settings)


def register_settings_to_filters(app):
    @app.callback(
        Output('filter-static-container', 'children', allow_duplicate=True),
        Output('filter-additional-content', 'children', allow_duplicate=True),
        Output('filter-settings', 'data', allow_duplicate=True),
        Input('filter-settings', 'data'),
        prevent_initial_call=True
    )
    def settings_to_all_filters(filter_settings_json):
        # load in the settings and determine the trigger
        filter_settings = json.loads(filter_settings_json)
        actions = filter_settings['actions']    # determine the actions to do

        # check if no update needed
        if (actions == []):
            raise PreventUpdate

        # deal with static content
        static_return = (
            settings_to_filters(filter_settings, static=True) 
            if (STATIC_ACTION in actions)
            else no_update
        )

        # deal with the additional content
        additional_return = (
            settings_to_additional_filters_layout(filter_settings) 
            if (ADDITIONAL_ACTION in actions)
            else no_update
        )

        # make sure no more actions to do
        filter_settings['actions'] = []

        # return all the info
        return static_return, additional_return, json.dumps(filter_settings)


# ------------------------------- for changing the environment -------------------------------------

from pprint import pprint

# store for each child option store the options (either way)
# for each id,
def get_new_filter_settings(old_data_type, old_filter_settings, children_ids, children_values, data_dictionaries):
    # get the new filter settings creator
    new_filter_settings = old_filter_settings.copy()

    # unpack values from the children_ids
    active_filters = [child_id['filter'] for child_id in children_ids]
    active_filter_types = [child_id['type'] for child_id in children_ids]

    # reset the active filters
    new_filter_settings[old_data_type]['active'] = []

    # change each value in the dictionary
    for active_filter, active_filter_type, filter_value in zip(active_filters, active_filter_types, children_values):
        # change the options
        new_filter_settings[old_data_type]['value'][active_filter] = filter_value

        # save as active if additional
        if (active_filter_type == 'additional'):
            new_filter_settings[old_data_type]['active'].append(active_filter)
    
    # return the json as a string
    return json.dumps(new_filter_settings)


# return all the components
def get_new_additional_fitler_components(new_data_type, filter_settings, old_filter_components, data_dictionaries):
    # STATIC FILTERS
    # get the static filters involved
    static_filters = data_dictionaries[FILTER_TYPES][new_data_type]['static']

    # create the new components
    new_static_filters = []
    for static_filter in static_filters:
        static_filter_options = data_dictionaries[FILTER_TO_OPTIONS][new_data_type][static_filter]
        static_filter_value = filter_settings[new_data_type]['value'][static_filter]
        new_static_filters.append(
            create_static_filter(static_filter, static_filter_options, value=static_filter_value)
        )

    # additional FILTERS
    # find the active elements
    active_additional_filters = filter_settings[new_data_type]['active']

    # get the new filter components
    new_additional_filter = [old_filter_components[0]]      # this gets the dropdown for add_filter
    for active_filter in active_additional_filters:
        active_filter_options = data_dictionaries[FILTER_TO_OPTIONS][new_data_type][active_filter]
        active_filter_value = filter_settings[new_data_type]['value'][active_filter]
        new_additional_filter.append(
            create_additional_filter(active_filter, active_filter_options, value=active_filter_value)
        )
    
    # RETURN
    return new_static_filters, new_additional_filter


# get the new options for the available additional filters
def get_new_new_filter_options(new_data_type, filter_settings, data_dictionaries):
    additional_filters = data_dictionaries[FILTER_TYPES][new_data_type]['additional']
    return sorted(list(
        set(additional_filters) - set(filter_settings[new_data_type]['active'])
    ))


def register_change_dataset(app, data_dictionaries):
    @app.callback(
        Output('filter-static-container', 'children'),      # need to reload the BOTH the children
        Output('filter-additional-container', 'children'),     # "                                  "
        Output('add-filter-dropdown', 'options'),           # need to change the options as well
        Output('filter-settings', 'data', allow_duplicate=True),                  # make sure to change the filter settings
        Input('type-dropdown', 'value'),                    # get the type that's been changed
        State('filter-settings', 'data'),                   # get the current filter settings
        State({'class': 'filters', 'filter': ALL, 'role': 'column', 'type': ALL}, 'id'),        # will read in all the 'ids' of both types of filters
        State({'class': 'filters', 'filter': ALL, 'role': 'dropdown', 'type': ALL}, 'value'),   # will read in all options of both types of filters
        State('filter-additional-container', 'children'),      # need the first element for add-filter-dropdown
        prevent_initial_call=True
    )
    def change_dataset(new_data_type, old_filter_settings_json, children_ids, children_values, old_filter_components):
        old_data_type = list(set(['interview', 'offer']) - set([new_data_type]))[0]
        old_filter_settings = json.loads(old_filter_settings_json)

        # get all the new components
        new_filter_settings = get_new_filter_settings(
            old_data_type, old_filter_settings, children_ids, children_values, data_dictionaries
        )
        new_static_filters, new_additional_filters = get_new_additional_fitler_components(
            new_data_type, old_filter_settings, old_filter_components, data_dictionaries
        )
        new_new_filter_options = get_new_new_filter_options(
            new_data_type, old_filter_settings, data_dictionaries
        )

        # return everything, changing the python object to a json string
        return new_static_filters, new_additional_filters, new_new_filter_options, json.dumps(new_filter_settings)


def register_callbacks(app, data_dictionaries):
    # adding filters and what not
    register_adjust_new_filters(app)
    register_delete_filter(app, data_dictionaries)
    register_toggle_additional_filters(app)

    # big changer
    register_settings_to_filters(app)

    # switching settings
    register_change_dataset(app, data_dictionaries)

