# main components for callbacks
from dash import dcc
from dash.dependencies import Input, Output, State
from dash import callback_context, no_update
from dash.exceptions import PreventUpdate

# regular operations
import pandas as np
import numpy as np
import json

# image operations
import tempfile
import os
import base64
from PIL import Image
from io import BytesIO

# own functions
from .callback_header import *


# --------------------------------- GIF GENERATION -----------------------------------


def create_gif_from_base64_images(base64_images, output_path, interval):
    """Decode base64 images and create a GIF."""
    frames = []
    for b64 in base64_images:
        # Remove the "data:image/png;base64," prefix
        base64_data = b64.split(",")[1]
        image_data = base64.b64decode(base64_data)
        img = Image.open(BytesIO(image_data))
        frames.append(img.convert("RGB"))  # Ensure compatibility
    
    # create the durations
    interval_ms = interval * 1000
    interval_last_ms = interval_ms * 2

    # Create a duration list
    durations = [interval_ms] * (len(frames) - 1) + [interval_last_ms]

    # Save frames as a GIF
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=durations,  # 500 ms per frame
        loop=0,  # Infinite loop
    )


def generate_gif_src(carousel_settings):
    # get the images
    base64_images = [item["src"] for item in carousel_settings["items"]]

    # have the temporary file
    temp_dir = tempfile.mkdtemp()
    gif_path = os.path.join(temp_dir, "carousel.gif")

    # Generate the GIF
    create_gif_from_base64_images(base64_images, gif_path, carousel_settings['interval'])

    # Read GIF and encode it to base64 for display
    with open(gif_path, "rb") as gif_file:
        gif_base64 = base64.b64encode(gif_file.read()).decode()

    # Return the base64-encoded GIF
    return f"data:image/gif;base64,{gif_base64}"


# ------------------------------------ CALLBACKS BUTTONS ---------------------------------


def register_create_gif_callback(app):
    @app.callback(
        Output('carousel-settings', 'data', allow_duplicate=True),
        Input('carousel-slides-save-gif', 'n_clicks'),
        State('carousel-settings', 'data'),
        prevent_initial_call=True
    )
    def create_gif_callback(n_clicks, carousel_settings_json):
        # load in the data
        carousel_settings = json.loads(carousel_settings_json)

        # change the actions
        carousel_settings['actions'] = [GIF_ACTION]

        return json.dumps(carousel_settings)


def register_update_interval(app):
    @app.callback(
        Output('carousel-settings', 'data', allow_duplicate=True),
        Input('carousel-gif-interval', 'value'),
        State('carousel-settings', 'data'),
        prevent_initial_call=True
    )
    def update_interval(new_interval, carousel_settings_json):
        # load in the data
        carousel_settings = json.loads(carousel_settings_json)

        # check the interval isn't 0
        if (new_interval == 0):
            raise PreventUpdate

        # change the new interval
        carousel_settings['interval'] = new_interval

        # change the actions
        carousel_settings['actions'] = [GIF_ACTION]

        return json.dumps(carousel_settings)


# ------------------------------------ CALLBACKS IMPORTANT -------------------------------


def register_carousel_settings_to_layout(app):
    @app.callback(
        Output('carousel-slides', 'items'),
        Output('carousel-gif-display', 'src'),
        Input('carousel-settings', 'data'),
        prevent_initial_call=True
    )
    def carousel_settings_to_layout(carousel_settings_json):
        # load in the data
        carousel_settings = json.loads(carousel_settings_json)

        # check slide action
        carousel_slides_return = (
            carousel_settings['items']
            if CAROUSEL_ACTION in carousel_settings['actions']
            else no_update
        )

        # check the gif action if any
        carousel_gif_return = (
            generate_gif_src(carousel_settings)
            if GIF_ACTION in carousel_settings['actions']
            else no_update
        )

        # check the other actions
        return carousel_slides_return, carousel_gif_return


# ------------------------------------ FINAL REGISTRY ------------------------------------


def register_callbacks(app):
    # buttons
    register_create_gif_callback(app)
    register_update_interval(app)

    # main callbacks
    register_carousel_settings_to_layout(app)