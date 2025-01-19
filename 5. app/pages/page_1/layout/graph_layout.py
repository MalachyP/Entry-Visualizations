from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc

# will make the width 8 when full page
HOVER_RESET = 'reset the graph'
HOVER_SAVE = 'save the graph to image carousel'
HOVER_DOWNLOAD = 'download image as jpg'

# create the default option
DEFAULT_LEGEND_OPTION = 'success'

# ------------------------- COMPONENT FUNCTIONS -----------------------------------------------

# will output a column containing a graph
# - graph_type: whether it's the simple or the advanced
# - width: how wide the graph element is (6 for 2 and 8 for 1 I believe)
# - options: the options for the custom legend
def create_graph_component(graph_type, width, legend_options, figure=None, id_overide=False):
    if (not id_overide):
        graph_id = {'class': 'graph', 'type': graph_type, 'role': 'graph'}
    else:
        graph_id = id_overide

    return dbc.Col(
        # the stack for the top bar, graph and legend type 
        dbc.Stack(
            [
                # the graph component
                dcc.Graph(id=graph_id, figure=figure),

                # the stack for reset button, download button, save to image carousel
                html.Div(
                    [
                        # the legend option (in div to grow)
                        html.Div(
                            dcc.Dropdown(
                                options=legend_options,
                                value=DEFAULT_LEGEND_OPTION,
                                placeholder=DEFAULT_LEGEND_OPTION,
                                id={'class': 'graph', 'type': graph_type, 'role': 'legend-dropdown'}
                            ),
                            className='flex-grow-1'
                        ),

                        # reset basically
                        dbc.Button(
                            'reset',
                            title=HOVER_RESET,
                            id={'class': 'graph', 'type': graph_type, 'role': 'reset-button'}
                        ),
                        dbc.Button(
                            'save',
                            title=HOVER_SAVE,
                            id={'class': 'graph', 'type': graph_type, 'role': 'save-image'}
                        ),
                        dbc.Button(
                            html.I(className="bi bi-download"),
                            title=HOVER_DOWNLOAD,
                            id={'class': 'graph', 'type': graph_type, 'role': 'download'}
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


# ------------------------------- LAYOUT FUNCTIONS -------------------------------------


# will supply a list of datasets, to create a graph layout essentially
def create_graph_layout(figs):
    if (len(figs) == 1):
        return dbc.Row(
            [create_graph_component('simple', 8, ['Yes', 'No'], figure=figs[0])],
            id='graph-container',
            justify='center'
        )
    else:
        return dbc.Row(
            [create_graph_component('simple', 6, ['Yes', 'No'], figure=fig) for fig in figs],
            id='graph-container',
            justify='center'
        )

# ------------------------------- CREATING DEFAULT VALUES -------------------------------------


def create_default_graph():
    return [
        # create the single column
        create_graph_component('simple', 8, ['Yes', 'No'], id_overide='scatter-plot-simple')
    ]