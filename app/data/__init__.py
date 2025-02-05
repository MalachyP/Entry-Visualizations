# IMPORTANT FUNCTIONS TO RUN
# - `filtering`
#   - `create_filters`([interview_df], [offer_df]) will pre filter all of the data base
#     on the unis. First keys are the data type, and this will return a dictionary, where
#     the keys will be different uni names and the values will be filtered dataframes
#
# - `options`
#   - `create_filter_to_options`([interview_df], [offer_df]) will return a dictionary where
#     the first keys are the dataset type, and the second key will be the filter options, with
#     corresponding values of all the possible values
#
# - `parameters`
#   - will contain all the parameters for the variables
#
# - `other`
#   - `create_default_json`([filter_to_options_dict]) will initialize the json used in store

from . import filtering
from . import options
from . import parameters