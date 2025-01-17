# core components for container
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc

import json

# names of dictionary data functions
FILTER_TO_OPTIONS = "filter_to_options"
FILTER_TYPES = "filter_types"
DEFAULT_JSON = "default_json"

from .layout import filter_layout, graph_layout

# ---------------------------- HEADER --------------------------------------------------------------

def create_head_layout():
    return [
        html.Div(
            html.H1('Investigation into medicine entry'),
            style={
                'display': 'flex',
                'justifyContent': 'center',
                'alignItems': 'center',
                'width': '100%'
            }
        ),

        html.Hr()
    ]


# ----------------------- FILTERING COMPONENTS ------------------------------------------------------

def create_dataset_layout():
    return [
        html.H3('Dataset Type'),
        # the starting filter
        dbc.Row([
            dbc.Col(
                dcc.Dropdown(
                    id='type-dropdown',
                    options=['interview', 'offer'],
                    value='interview',
                ),
                width=4
            ),
            dbc.Col(
                dbc.Checklist(
                    options=["Enable Extra Filters"],
                    value=[],
                    switch=True,
                    id='toggle-additional-filters'
                ),
                width="auto"
            )
        ])
    ]


def create_filters_layout(data_dictionaries):
    return [
        html.H3('Filters'),

        # storage for switching between
        dcc.Store(
            id='filter-settings',
            #storage_type='local',
            data=filter_layout.create_default_json(data_dictionaries[FILTER_TO_OPTIONS],
                                                   data_dictionaries[FILTER_TYPES])
        ),

        # filter conainer basically
        dbc.Container(
            dbc.Row(
                filter_layout.create_default_static(data_dictionaries),
                id='filter-static-container',
                justify='start'
            ),
            fluid=True
        ),

        html.Br(),

        # used to store the content for dynamically created content (toggle)
        html.Div(id='filter-additional-content')
    ]


# ----------------------- GRAPH COMPONENTS ---------------------------------------------------

def create_graph_layout():
    return [
        # graph container
        dbc.Row(
            graph_layout.create_default_graph(),
            id='graph-container', 
            justify='center'
        ),

        # displayed information
        html.H1("Display DataFrame in Dash"),
        dash_table.DataTable(
            id='graph-info',
            style_table={'overflowX': 'auto'},  # Make table scrollable if too wide
            style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
            style_cell={'textAlign': 'left'}
        ),

        # the stored data frame
        dcc.Store(id='graph-frame')
    ]

# ----------------------- LAYOUT FUNCTION -------------------------------------------------

def create_layout(data_dictionaries):
    # Layout with filters
    return html.Div([
        *create_head_layout(),
        *create_dataset_layout(),
        *create_filters_layout(data_dictionaries),
        *create_graph_layout()
        ])