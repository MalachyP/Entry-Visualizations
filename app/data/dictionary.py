from . import options, parameters, filtering

def get_data_dictionaries(interview_df, offer_df):
        # initalize the data functions
    # - `filter_to_options`:    options of each filter
    # - `filter_types`:         static/dynamic filters for each datasets
    # - `data_views`:           the data views for each dataset and uni option
    data_dictionaries = {
        # dictionaries to determine the types of data
        "filter_to_options": options.create_filter_to_options(interview_df, offer_df), 
        "filter_types": parameters.FILTER_TYPES,
        "display_info": parameters.DISPLAY_INFO,
        "legend_options": parameters.LEGEND_OPTIONS,
        "options_order_overide": parameters.ORDER_OVERIDE,
        "missing_columns": options.MISSING_OPTIONS,

        # precomputed views of the frame and the originals 
        "data_views": filtering.create_filters(interview_df, offer_df),
        'original_frames': {'interview': interview_df, 'offer': offer_df}
    }

    # update with legened options
    data_dictionaries = data_dictionaries | {
        'legend_gradients': options.create_legend_options(data_dictionaries['filter_to_options'])
    }

    return data_dictionaries