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
import io
import base64
from PIL import Image
from io import BytesIO

# own functions
from .callback_header import *

# --------------------------------- HELPER FUNCTIONS ----------------------------------


def source_to_download(src, file):
     # Remove metadata (if present)
    pure_base64 = src.split("base64,")[1]

    # Decode Base64 and prepare as a file
    decoded_image = base64.b64decode(pure_base64)

    # Return the file for download
    return dcc.send_bytes(decoded_image, file)


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
    base64_images = carousel_settings['gif items']

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


# --------------------------------------- CALLBACK HELPERS --------------------------------------


def register_alter_slide_index(app):
    @app.callback(
        Output('carousel-settings', 'data', allow_duplicate=True),
        Input('carousel-slides', 'active_index'),
        State('carousel-settings', 'data'),
        prevent_initial_call=True
    )
    def alter_slide_index(new_active_index, carousel_settings_json):
        # load the settings
        carousel_settings = json.loads(carousel_settings_json)

        # check if update is necessary
        if (carousel_settings['active index'] == new_active_index):
            raise PreventUpdate
        
        # change the settings and return
        carousel_settings['active index'] = new_active_index

        # make sure no more changes
        carousel_settings['actions'] = []

        return json.dumps(carousel_settings)


# ------------------------------------ CALLBACKS BUTTONS SLIDES ---------------------------------


def register_move_slides_backwards(app):
    @app.callback(
        Output('carousel-settings', 'data', allow_duplicate=True),  # output is the settings of course
        Input('carousel-slides-move-backwards', 'n_clicks'),        # move back input
        State('carousel-settings', 'data'),     # get the carousel settings so can update
        prevent_initial_call=True
    )
    def move_slides_backwards(_, carousel_settings_json):
        # load the settings
        carousel_settings = json.loads(carousel_settings_json)
        old_active_index = carousel_settings['active index']

        # get all the items
        old_items = carousel_settings['slide items']

        # check that it's not the last item (but also check if nothing in there)
        if (old_active_index == 0 or len(old_items) <= 1):
            raise PreventUpdate
        
        # in this case, split the items of course
        new_start = old_items[:old_active_index - 1]
        new_end = [old_items[old_active_index - 1]] + old_items[old_active_index + 1:]
        new_items = new_start + [old_items[old_active_index]] + new_end

        # change carousel settings
        carousel_settings['slide items'] = new_items

        # get the new index
        carousel_settings['active index'] = old_active_index - 1

        # make sure activating the right action
        carousel_settings['actions'] = [CAROUSEL_ACTION]

        return json.dumps(carousel_settings)


def register_move_slides_forwards(app):
    @app.callback(
        Output('carousel-settings', 'data', allow_duplicate=True),  # output is the settings of course
        Input('carousel-slides-move-forwards', 'n_clicks'),        # move back input
        State('carousel-settings', 'data'),     # get the carousel settings so can update
        prevent_initial_call=True
    )
    def move_slides_forwards(_, carousel_settings_json):
        # load the settings
        carousel_settings = json.loads(carousel_settings_json)
        old_active_index = carousel_settings['active index']

        # get all the items
        old_items = carousel_settings['slide items']

        # check that it's not the last item (use the minimum for the start)
        if (old_active_index == len(old_items) - 1 or len(old_items) <= 1):
            raise PreventUpdate
        
        # in this case, split the items of course
        new_start = old_items[:old_active_index] + [old_items[old_active_index + 1]]
        new_end = old_items[old_active_index + 2:]
        new_items = new_start + [old_items[old_active_index]] + new_end

        # change carousel settings
        carousel_settings['slide items'] = new_items

        # get the new index
        carousel_settings['active index'] = old_active_index + 1

        # make sure activating the right action
        carousel_settings['actions'] = [CAROUSEL_ACTION]

        return json.dumps(carousel_settings)


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

        # ensure that there are at least some files
        if (carousel_settings['slide items'] == []):
            raise PreventUpdate

        # register the gif as active
        carousel_settings['gif items'] = [item["src"] for item in carousel_settings['slide items']]

        # change the actions
        carousel_settings['actions'] = [GIF_ACTION]

        return json.dumps(carousel_settings)


def register_delete_slide(app):
    @app.callback(
        Output('carousel-settings', 'data', allow_duplicate=True),  # output is the settings of course
        Input('carousel-slides-delete', 'n_clicks'),        # move back input
        State('carousel-settings', 'data'),     # get the carousel settings so can update
        prevent_initial_call=True
    )
    def delete_slide(_, carousel_settings_json):
        # load the data
        carousel_settings = json.loads(carousel_settings_json)
        old_active_index = carousel_settings['active index']

        # check to see not stuck as default
        if (carousel_settings['slide items'] == []):
            raise PreventUpdate

        # delete the current item
        carousel_settings['slide items'].pop(old_active_index)

        # get the new active index (make sure it is within [0, max_index])
        new_active_index = min(old_active_index, len(carousel_settings['slide items']) - 1)
        new_active_index = max(new_active_index, 0)
        carousel_settings['active index'] = new_active_index

        # make sure activating the right action
        carousel_settings['actions'] = [CAROUSEL_ACTION]

        return json.dumps(carousel_settings)


def register_clear_slides(app):
    @app.callback(
        Output('carousel-settings', 'data', allow_duplicate=True),  # output is the settings of course
        Input('carousel-slides-clear', 'n_clicks'),        # move back input
        State('carousel-settings', 'data'),     # get the carousel settings so can update
        prevent_initial_call=True
    )
    def clear_slides(_, carousel_settings_json):
        # load the settings
        carousel_settings = json.loads(carousel_settings_json)

        # check if no update needed
        if (carousel_settings['slide items'] == []):
            raise PreventUpdate

        # clear the items
        carousel_settings['slide items'] = []

        # reset the active index
        carousel_settings['active index'] = 0

        # make sure the update the actions
        carousel_settings['actions'] = [CAROUSEL_ACTION]

        return json.dumps(carousel_settings)


def register_download_slide(app):
    @app.callback(
        Output('download', 'data', allow_duplicate=True),
        Output('carousel-settings', 'data', allow_duplicate=True),
        Input('carousel-slides-download', 'n_clicks'),
        State('carousel-settings', 'data'),
        prevent_initial_call=True
    )
    def download_slide(_, carousel_settings_json):
        # load settings
        carousel_settings = json.loads(carousel_settings_json)

        # make sure not to update if default
        if (carousel_settings['slide items'] == []):
            raise PreventUpdate

        # get the current source
        active_src = carousel_settings['slide items'][carousel_settings['active index']]['src']

        # get the current file
        slide_bytes = source_to_download(active_src, DEFAULT_IMG_DOWNLOAD)

        # no more further actions
        carousel_settings['actions'] = []

        return slide_bytes, json.dumps(carousel_settings)


# ------------------------------------ CALLBACKS BUTTONS GIF ------------------------------------


# will basically always be registering the update (unless new value is 0). The action will be
# gif action because it has to be. Just doesn't necessarily create a gif if no gif items
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


def register_clear_gif(app):
    @app.callback(
        Output('carousel-settings', 'data', allow_duplicate=True),
        Input('carousel-gif-clear', 'n_clicks'),
        State('carousel-settings', 'data'),
        prevent_initial_call=True
    )
    def clear_gif(_, carousel_settings_json):
        # load in the data
        carousel_settings = json.loads(carousel_settings_json)

        # don't need to send back data if already inactive
        if (carousel_settings['gif items'] == []):
            raise PreventUpdate
                
        # set to false and ensure update action occurs
        carousel_settings['gif items'] = []
        carousel_settings['actions'] = [GIF_ACTION]

        return json.dumps(carousel_settings)


def register_download_gif(app):
    @app.callback(
        Output('download', 'data'),
        Input('carousel-gif-download', 'n_clicks'),
        State('carousel-gif-display', 'src'),
        State('carousel-settings', 'data'),
        prevent_initial_call=True
    )
    def download_gif(_, gif_src, carousel_settings_json):
        # load the settings
        carousel_settings = json.loads(carousel_settings_json)

        # if not active, don't update
        if (carousel_settings['gif items'] == []):
            raise PreventUpdate

        # get the current file
        gif_bytes = source_to_download(gif_src, DEFAULT_GIF_DOWNLOAD)

        return gif_bytes


# ------------------------------------ CALLBACKS IMPORTANT -------------------------------


# This will be a weird callback as they use different methods
# - carousel-slides: will save the images from settings, and if blank decide what to do
#                    in other words, have the images and src saved in settings
# - carousel-gif   : will have no intermediate value apart from a true of false indictating
#                    whether this component is active or not, to determine whether to create
#                    a new gif or not
def register_carousel_settings_to_layout(app):
    @app.callback(
        Output('carousel-slides', 'items'),
        Output('carousel-slides', 'active_index'),
        Output('carousel-gif-display', 'src'),
        Input('carousel-settings', 'data'),
    )
    def carousel_settings_to_layout(carousel_settings_json):
        # load in the data
        carousel_settings = json.loads(carousel_settings_json)

        # SLIDE ACTIONS
        if (not CAROUSEL_ACTION in carousel_settings['actions']):
            # check to see if not meant to update
            carousel_slides_return = no_update
            carousel_active_index_return = no_update

        elif (len(carousel_settings['slide items']) == 0):
            # check to see if should set to default because no slides
            carousel_slides_return = DEFAULT_CAROUSEL_SLIDES
            carousel_active_index_return = 0    # this is the correct index of course

        else:
            # return the true items
            carousel_slides_return = carousel_settings['slide items']
            carousel_active_index_return = carousel_settings['active index']

        # GIF ACTIONS
        if (not GIF_ACTION in carousel_settings['actions']):
            # check if no update needed
            carousel_gif_return = no_update
        
        elif (carousel_settings['gif items'] == []):
            # check if the gif is not meant to be active
            carousel_gif_return = DEFAULT_CAROUSEL_GIF

        else:
            # return the proper gif
            carousel_gif_return = generate_gif_src(carousel_settings)

        # check the other actions
        return carousel_slides_return, carousel_active_index_return, carousel_gif_return


# ------------------------------------ FINAL REGISTRY ------------------------------------


def register_callbacks(app):
    # helper callbacks
    register_alter_slide_index(app)

    # slide buttons
    register_move_slides_backwards(app)
    register_move_slides_forwards(app)
    register_create_gif_callback(app)
    register_delete_slide(app)
    register_clear_slides(app)
    register_download_slide(app)

    # gif buttons
    register_update_interval(app)
    register_download_gif(app)
    register_clear_gif(app)

    # main callbacks
    register_carousel_settings_to_layout(app)