# layout packages
from dash import dcc, html
import dash_bootstrap_components as dbc

# regular packages
import json

# my own functions
from .layout_parameters import *


def create_carousel_settings():
    return json.dumps({
        "items": [],
        "interval": 1.5,
        "actions": [],
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
                html.Div([
                    dbc.Button(
                        "move forward",
                        id='carousel-slides-move-forward'
                    ),
                    dbc.Button(
                        "move backwards",
                        id='carousel-slides-move-backwards'
                    ),
                    dbc.Button(
                        "create gif",
                        id='carousel-slides-save-gif'
                    ),
                    dbc.Button(
                        "delete",
                        id='carousel-slides-delete'
                    ),
                    dbc.Button(
                        "clear all",
                        id='carousel-slides-clear'
                    )
                ])
            ]
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

                        # download button
                        dbc.Button(
                            "download",
                            id='carousel-gif-download'
                        ),
                        
                        # delete button
                        dbc.Button(
                            "delete",
                            id='carousel-gif-delete'
                        )
                    ],
                    direction="horizontal",
                    gap=1
                )
            ]
        ),
        width=6
    )

