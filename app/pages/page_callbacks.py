from . import main_page

def register_callbacks(app, data_dictionaries):
    main_page.page_callbacks.register_callbacks(app, data_dictionaries)