# layout packages
from dash import dcc, html
import dash_bootstrap_components as dbc

# regular packages
import json

# my own functions
from .layout_parameters import *

CAROUSEL_ACTION = 'carousel'
GIF_ACTION = 'gif'

def create_carousel_settings():
    return json.dumps({
        "items": [],
        "gif active": False,
        "interval": 1.5,
        "actions": [CAROUSEL_ACTION, GIF_ACTION]
    })


def create_carousel_slides():
    return dbc.Col(
        dbc.Stack(
            [
                dbc.Carousel(
                    items=[], # will be filled in by the callback
                    id='carousel-slides',
                    indicators=True,
                    controls=True,
                    className="carousel-fade",
                    style={"backgroundColor": "#333"}
                    #slide=False
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Button(
                                    html.I(className='bi bi-arrow-left-square'),
                                    id='carousel-slides-move-forward',
                                    className='m-1'
                                ),
                                dbc.Button(
                                    html.I(className='bi bi-arrow-right-square'),
                                    id='carousel-slides-move-backwards',
                                    className='me-1'
                                ),
                                dbc.Button(
                                    "create gif",
                                    id='carousel-slides-save-gif'
                                )
                            ],
                            width="auto"
                        ),

                        # Spacer (creates the gap)
                        dbc.Col(width=True),

                        # content at the end of page
                        dbc.Col(
                            [
                                dbc.Button(
                                    html.I(className='bi bi-trash'),
                                    id='carousel-slides-delete'
                                ),
                                dbc.Button(
                                    "clear",
                                    id='carousel-slides-clear',
                                    className='m-1'
                                ),
                                dbc.Button(
                                    html.I(className="bi bi-download"),
                                    id='carousel-slides-download',
                                    className='me-1'
                                )
                            ],
                            width="auto"
                        )
                    ],
                    align="center",  # Vertically align items in the row
                    className="g-0",  # Remove extra gutter between rows
                )
            ],
            gap=2
        ),
        width=6
    )


def create_carousel_gif():
    return dbc.Col(
        dbc.Stack(
            [
                html.Img(
                    id='carousel-gif-display'
                ),
                dbc.Stack(
                    [
                    # the dragging component
                    html.Div(
                        [
                            dbc.Stack(
                                [
                                    html.B('select time interval', className='justify-content-center'),
                                    dcc.Slider(
                                        min=0, 
                                        max=5,
                                        value=1.5,
                                        id='carousel-gif-interval'
                                    )
                                ],
                                gap=1
                            )],
                            className='flex-grow-1'
                        ),
                        
                        # delete button
                        dbc.Button(
                            "clear",
                            id='carousel-gif-clear'
                        ),
                                                # download button
                        dbc.Button(
                            html.I(className="bi bi-download"),
                            id='carousel-gif-download',
                            className='me-1'
                        )
                    ],
                    direction="horizontal",
                    gap=1
                )
            ]
        ),
        width=6
    )

