from dash import dcc, html
import dash_bootstrap_components as dbc

import json
from pprint import pprint

from . import layout_parameters
from ..callbacks.callback_header import *
from .layout_parameters import *

# names of dictionary data functions
FILTER_TO_OPTIONS = "filter_to_options"
FILTER_TYPES = "filter_types"
DEFAULT_JSON = "default_json"

UNIVERSITY = "university"
#UNIVERSITY_OPTION = "Deakin University"
UNIVERSITY_OPTION = "The University of Melbourne"
#UNIVERSITY_OPTION = "The University of Queensland (Metro)"

YEAR = "year"
YEAR_OPTION = 2024

# ---------------------------- HELPER FUNCTIONS ---------------------------------------------

def is_multiselect(filter):
    return not filter in layout_parameters.SINGLE_OPTION_FILTERS

# ----------------------------- CREATING FILTER COMPONENTS -------------------------------------

def get_filter_name(filter_name):
    # look up in dictionary first
    if (filter_name in layout_parameters.filter_to_title):
        return layout_parameters.filter_to_title[filter_name]
    
    # covert every first word to upper case (space in front)
    filter_words = filter_name.split(" ")
    new_filter_words = [filter_word[0].upper() + filter_word[1:] for filter_word in filter_words]
    new_filter_name = " ".join(new_filter_words)

    filter_words = filter_name.split("(")
    new_filter_words = [filter_word[0].upper() + filter_word[1:] for filter_word in filter_words]
    new_filter_name = "(".join(new_filter_words)

    return new_filter_name


def get_default_value(filter_name, options):
    if (filter_name in layout_parameters.START_BLANK):
        return []
    elif (is_multiselect(filter_name)):
        return options
    else:
        return options[0]


def create_static_filter(new_filter, options, value='__default__'):
    # deal with the default value
    if (new_filter == UNIVERSITY):
        value = UNIVERSITY_OPTION
    elif (new_filter == YEAR):
        value = YEAR_OPTION
    elif (value == '__default__'):
        value = get_default_value(new_filter, options)
            
    return dbc.Col(
        dbc.Stack([
                html.B(get_filter_name(new_filter)),
                dcc.Dropdown(
                    id={'class': 'filters', 'filter': new_filter, 'role': 'dropdown', 'type': 'static'},
                    options=options,
                    multi=is_multiselect(new_filter),
                    value=value,
                    style={'width': '100%'}
                )
            ],
            gap=1
        ),
        id={'class': 'filters', 'filter': new_filter, 'role': 'column', 'type': 'static'},
        width=4
    )


def create_additional_filter(new_filter, options, value='__default__'):
    # deal with the default value
    if (value == '__default__'):
        value = get_default_value(new_filter, options)

    return dbc.Col(
        dbc.Stack([
                html.B(get_filter_name(new_filter)),
                dbc.Stack([
                        dcc.Dropdown(
                            id={'class': 'filters', 'filter': new_filter, 'role': 'dropdown', 'type': 'additional'},
                            options=options,
                            placeholder=layout_parameters.PLACEHOLDER,
                            multi=is_multiselect(new_filter),
                            value=value,
                            style={'width': '100%'}
                        ),
                        dbc.Button(
                            'Del',
                            id={'class': 'filters', 'filter': new_filter, 'role': 'delete-button'},
                            style={'width': '20%'},
                            className="bg-warning border rounded-pill"
                        )
                    ],
                    direction='horizontal',
                    gap=1
                )
            ],
            gap=1
        ),
        id={'class': 'filters', 'filter': new_filter, 'role': 'column', 'type': 'additional'},
        width=4
    )


def create_select_new_filter(filter_settings):
    # get the data type
    data_type = filter_settings['data type']

    # get the inactive filters
    inactive_filters = sorted(list(
        set(filter_settings[data_type]['additional value'].keys()) - set(filter_settings[data_type]['active'])
    ))

    return dbc.Col(
        dbc.Stack([
                html.B('Add New Filter'),
                dcc.Dropdown(
                    id='add-filter-dropdown', 
                    options=inactive_filters
                )
            ],
            gap=1 
        ),
        width=4
    )


# ------------------------------- CREATING FILTERS CONTENT -----------------------------------


def settings_to_filters(filter_settings, data_dictionaries, static=False):
    # get the data type in use
    data_type = filter_settings['data type']

    # create each active filters
    filter_components = []

    if (static == False):
        # add the add new filter component
        filter_components.append(create_select_new_filter(filter_settings))

        # get the main filters
        for active_filter in filter_settings[data_type]['active']:
            # get the active filter component
            active_filter_options = data_dictionaries[FILTER_TO_OPTIONS][data_type][active_filter]
            active_filter_value = filter_settings[data_type]['additional value'][active_filter]
            active_filter_component = create_additional_filter(
                active_filter, active_filter_options, value=active_filter_value
            )

            # append to the list
            filter_components.append(active_filter_component)

    else:
        for static_filter, static_filter_value in filter_settings[data_type]['static value'].items():        
            # get the new static filter
            active_filter_options = data_dictionaries[FILTER_TO_OPTIONS][data_type][static_filter]
            static_filter_component = create_static_filter(
                static_filter, active_filter_options, value=static_filter_value
            )

            # append to the list
            filter_components.append(static_filter_component)

    return filter_components


def settings_to_additional_filters_layout(filter_settings, data_dictionaries):
    # check if disabled
    if (filter_settings['additional filters'] == False):
        return []

    # this is the case where they are enabled
    return [
        html.H3('Additional Filters', className='title'),

        # filter container basically
        dbc.Container(
            dbc.Row(
                settings_to_filters(filter_settings, data_dictionaries, static=False),
                id='filter-additional-container',
                justify='start'
            ),
            fluid=True
        ),

        html.Br()
    ]


# ------------------------------- CREATING DEFAULT VALUES -------------------------------------


def correct_filter_option(filter_name, filter_options):
    if (filter_name == UNIVERSITY):
        return UNIVERSITY_OPTION
    elif (filter_name == YEAR):
        return YEAR_OPTION
    else:
        return filter_options[0]


def create_default_json(filter_to_options, filter_types):
    # get most of the default options
    default_dict =  {
        data_type: {
            'active': [],
            'static value': {
                filter_name: filter_options 
                for filter_name, filter_options in filter_to_options[data_type].items()
                if is_multiselect(filter_name) and filter_name in filter_types[data_type]['static'] # this will return a dictionary of filters to options
            } | {
                filter_name: correct_filter_option(filter_name, filter_options)
                for filter_name, filter_options in filter_to_options[data_type].items()
                if not is_multiselect(filter_name) and filter_name in filter_types[data_type]['static'] # this will return a dictionary of filters to options
            }, 
            'additional value': {
                filter_name: filter_options 
                for filter_name, filter_options in filter_to_options[data_type].items()
                if is_multiselect(filter_name) and filter_name in filter_types[data_type]['additional'] # this will return a dictionary of filters to options
            } | {
                filter_name: filter_options[0] 
                for filter_name, filter_options in filter_to_options[data_type].items()
                if not is_multiselect(filter_name) and filter_name in filter_types[data_type]['additional'] # this will return a dictionary of filters to options
            },
            'legend': LEGEND_DEFAULT_OPTION
        }   
        for data_type in ['interview', 'offer']
    }

    # add information about the graph
    default_dict = default_dict | {
        'graph': {
            'type': GRAPH_DEFAULT_OPTION,
            'title': None
       }
    }

    # add extra information
    default_dict = default_dict | {
        'actions': [GRAPH_ACTION, GRAPH_DATA_ACTION],
        'additional filters': False,
        'data type': 'interview'
    }

    # for starting blank options, start blank (only for multiselect)
    for start_blank_filter in layout_parameters.START_BLANK:
        # iterate each data type
        for data_type in ['interview', 'offer']:
            # if not already existing, continue
            if (not default_dict[data_type]['static value'].get(start_blank_filter) is None):
                default_dict[data_type]['static value'][start_blank_filter] = []
            elif (not default_dict[data_type]['additional value'].get(start_blank_filter) is None):
                default_dict[data_type]['additional value'][start_blank_filter] = []
    
    # return the dumped json
    return json.dumps(default_dict)


# will return a list of components
def create_default_static(data_dictionaries):

    static_filter_components = []

    # iterate through static filters
    for static_filter in data_dictionaries[FILTER_TYPES]['interview']['static']:
        # get the current filter options and create the component
        static_filter_options = data_dictionaries[FILTER_TO_OPTIONS]['interview'][static_filter]
        static_filter_components.append(create_static_filter(static_filter, static_filter_options))
    
    return static_filter_components




