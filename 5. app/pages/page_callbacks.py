from . import page_1

def register_callbacks(app, data_dictionaries):
    page_1.page_callbacks.register_callbacks(app, data_dictionaries)