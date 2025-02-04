import pandas as pd
import numpy as np
import matplotlib.colors as mcolors

from .filtering import create_options
from . import parameters

THRESHOLD = 8
SPLIT_START = 4

START_COLOUR = "#636EFA" # plotly blue
END_COLOUR = "#EF553B"   # plotly red
NONE_COLOUR = "#d3d3d3"  # plotly light grey

# --------------------------------- FILTER TO OPTIONS ----------------------------------------


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
            # make sure no nans are here (should be dealt with elsewhere)
            assert not any([pd.isna(x) for x in array])

            # sort like normal
            if ('None' in array):
                return sorted([x for x in array if not x == 'None']) + ['None']
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
                filter_to_options[data_type][filter] = [str(x) for x in list(range(1, 7))]
            elif (filter == "success"):
                filter_to_options[data_type][filter] = ["Yes", "No"]
            elif (filter in parameters.ORDER_OVERIDE):
                # figure out if a specific order required
                filter_to_options[data_type][filter] = parameters.ORDER_OVERIDE[filter]
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


# -------------------------------- CREATING THE LEGEND ---------------------------------------


def get_weightings(n_options):
    # make sure 1 or above
    if (n_options <= 0):
        raise ValueError(n_options)

    # account for the singleton
    if (n_options == 1):
        return [1]

    # Generate the conventionally
    if (n_options < THRESHOLD):
        return [i/(n_options-1) for i in range(n_options)]

    # create the starting array
    weightings = np.zeros(n_options)

    # assign the first part of the array
    for idx in range(SPLIT_START):
        weightings[idx] = idx

    # figure out the number of chunks to assign
    n_chunks = int(np.ceil( np.log(n_options - SPLIT_START) / np.log(2) ))

    for n_chunk in range(1, n_chunks + 1):
        # using basically maths, adding the previous parts
        start = SPLIT_START + (2 ** n_chunk - 2)

        # end will be the start, but remember the true end, 
        end = min(start + 2 ** n_chunk - 1, n_options - 1)

        for idx in range(start, end + 1):
            # subtract - 1, as want to start at split_start
            weightings[idx] = SPLIT_START + n_chunk - 1
    
    # divide by the highest value
    weightings = weightings / weightings[-1]

    # convert to python type
    weightings = [float(x) for x in weightings]

    return weightings


def generate_gradient(n_options):
    def colorFader(c1,c2,mix=0): #fade (linear interpolate) from color c1 (at mix=0) to c2 (mix=1)
        c1=np.array(mcolors.to_rgb(c1))
        c2=np.array(mcolors.to_rgb(c2))
        return mcolors.to_hex((1-mix)*c1 + mix*c2)

    # get the gradient
    gradient = [colorFader(START_COLOUR, END_COLOUR, weight) for weight in get_weightings(n_options)]        

    return gradient


def create_legend_options(filter_to_options):
    # the out thing (can be divided, even if not optimal)
      # can pull the data type value directly in the future
    out = {"interview": {}, "offer": {}}

    # get each data type
    for data_type in out.keys():
        # get each legend option associated with the data type
        for legend_option in parameters.LEGEND_OPTIONS[data_type]:
            # assign legend_option options accordingly
            legend_option_options = (
                parameters.ORDER_OVERIDE[legend_option]
                if legend_option in parameters.ORDER_OVERIDE
                else filter_to_options[data_type][legend_option]
            )

            # (hoping it's already at the end of the pack if exists)
            if ('None' in legend_option_options):
                legend_option_gradients = generate_gradient(len(legend_option_options) - 1)
                legend_option_gradients.append(NONE_COLOUR)
            else:
                legend_option_gradients = generate_gradient(len(legend_option_options))

            # assign the ordering and mapping
            out[data_type][legend_option] = {
                'category order': {
                    legend_option: legend_option_options
                },
                'color map discrete': {
                    curr_option: curr_gradient
                    for curr_option, curr_gradient in zip(legend_option_options, legend_option_gradients)
                }
            }
    
    # finally return the out
    return out


# -------------------------------- THE MISSING OPTIONS ----------------------------------------

MISSING_OPTIONS = {
    'interview': {
        2022: [
            'uq tier', 'casper quartile', 
            'deakin tier', 'unimelb gam',
            'undf bonuses' , 'unds bonuses', 
            'uow bonuses'
        ],
        2023: [
            'undf bonuses' , 'unds bonuses',
            'deakin tier', 'unimelb gam',
            'uow bonuses'
        ],
        2024: []
    },
    'offer': {
        2022: [
            'interview prep hours'
        ],
        2023: []
    }
}