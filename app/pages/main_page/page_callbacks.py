from .callbacks import filter_callbacks
from .callbacks import graph_callbacks
from .callbacks import carousel_callbacks

def register_callbacks(app, data_dictionaries):
    filter_callbacks.register_callbacks(app, data_dictionaries)
    graph_callbacks.register_callbacks(app, data_dictionaries)
    carousel_callbacks.register_callbacks(app)