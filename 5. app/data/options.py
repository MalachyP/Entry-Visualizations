import pandas as pd
import numpy as np

from .filtering import create_options
from . import parameters


# Custom serializer function
def convert_numpy(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, list):
        return [convert_numpy(item) for item in obj]  # Recursively process lists
    elif isinstance(obj, dict):
        return {key: convert_numpy(value) for key, value in obj.items()}  # Process dicts
    return obj  # Return other types as-is


def create_get_unique_options(interview_df, offer_df):
    def get_unique_options_creator(filter):
        def sort_with_nan(array):
            if (any([pd.isna(x) for x in array])):
                return sorted([x for x in array if not pd.isna(x)]) + ['None']
            return sorted(array)

        options = []

        if (filter in interview_df.columns):
            options = interview_df[filter].unique()
        if (filter in offer_df.columns):
            if (not filter == "places selected"):
                options = list(set(options) | set(offer_df[filter].unique()))
            else:
                # Extract unique variables (not in interviews)
                options = ["BMP", "CSP", "FFP"]

        return sort_with_nan(options)


    return get_unique_options_creator


# get the unique options
def create_filter_to_options(interview_df, offer_df):
    # get the unique options
    get_unique_options = create_get_unique_options(interview_df, offer_df)

    # get the filters
    filters_to_find = {
        # should have no overlap
        "interview": parameters.ADDITIONAL_FILTERS["interview"] + parameters.STANDARD_FILTERS["interview"],
        "offer": parameters.ADDITIONAL_FILTERS["offer"] + parameters.STANDARD_FILTERS["offer"]
    }

    # initialize
    filter_to_options = {"interview": {}, "offer": {}}

    # get the uni options for later
    uni_options = create_options(interview_df, offer_df)

    # get the unique options
    for data_type in ["interview", "offer"]:
        for filter in filters_to_find[data_type]:
            # make sure to deal with university separately
            if (filter == "university"):
                filter_to_options[data_type][filter] = uni_options[data_type]
            elif (filter == "preference"):
                filter_to_options[data_type][filter] = list(range(1, 7))
            elif (filter == "success"):
                filter_to_options[data_type][filter] = ["Yes", "No"]
            elif (filter == "offer uni place type"):
                # exclude the none option
                filter_to_options[data_type][filter] = get_unique_options("offer uni place type")[:-1]
            elif (filter == 'places selected (include all)' or filter == 'places selected (exclude all)'):
                # don't need to exclude the none option
                filter_to_options[data_type][filter] = get_unique_options("places selected")
            elif (filter == 'year' and data_type == 'interview'):
                filter_to_options[data_type][filter] = list(range(2022, 2025))
            elif (filter == 'year' and data_type == 'offer'):
                filter_to_options[data_type][filter] = list(range(2022, 2024))
            else:
                # deal with reguarly
                filter_to_options[data_type][filter] = get_unique_options(filter)

    # convert everything to a python object
    return convert_numpy(filter_to_options)