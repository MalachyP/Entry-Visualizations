# -------------------------- DOWNLOADING -----------------------------------------

# SCHEMA
SCHEMA = {
    'interview': {
        # main
        'year': int,
        'preference': str,

        # bonuses
        'deakin bonus': str,
        'anu bonus': str,
        'mq bonus': str,
        'uow bonuses': str,
    },
    'offer': {
        # main
        'offer uni preference': str,
        'interview uni preference': str,
        'year': int,

        # bonuses
        'deakin bonus': str,
        'anu bonus': str,
        'mq bonus': str
    }
}

# --------------------------------- FILTERS --------------------------------------------

# for the creation of FILTER_TYPES
STANDARD_FILTERS = {
    'interview': ['university', 'year', 'rurality', 'success'],
    'offer': ['university', 'year', 'rurality', 'offer uni place type', 'success']
}
ADDITIONAL_FILTERS = {
    'interview': ['preference', 'casper quartile', 'deakin bonus', 'deakin tier', 'anu bonus', 'mq bonus', 'unimelb gam', 
                  'undf bonuses', 'unds bonuses', 'uow bonuses'],
    'offer': ['preference', 'interviewed?', 'interview opinion', 'interview prep hours', 'casper quartile', 'deakin bonus', 
              'anu bonus', 'mq bonus', 'uq rmp tier', 'places selected (include all)', 'places selected (exclude all)']
}

FILTER_TYPES = {
    data_type: {
        'static': STANDARD_FILTERS[data_type], 
        'additional': ADDITIONAL_FILTERS[data_type]
    }
    for data_type in ['interview', 'offer']
}

# --------------------------------- DATAFRAME ------------------------------------------

# For the information in the dataframe
DISPLAY_INFO = {
    'interview': [
        # identifying information
        'gamsat', 'gpa', 'combo', 'rurality',

        # information about the success
        'preference', 'success', 'notes',

        # bonuses
        'anu bonus', 'deakin bonus', 'deakin tier', 'mq bonus', 'undf bonuses', 'unds bonuses', 'unimelb gam', 'uow bonuses'
    ],
    'offer': [
        # identifying information
        'gamsat', 'gpa', 'combo', 'rurality', 'offer uni place type', 'places selected',

        # information about the success
        'preference', 'success', 'notes',

        # information about selection
        'interview uni', 'interview opinion', 'interview prep hours',

        # filtering info
        'anu bonus', 'casper quartile', 'deakin bonus'#, #'mq bonus', 'uq rmp tier'
    ]
}

# ---------------------------------- LEGEND --------------------------------------------

# for legend options
LEGEND_OPTIONS_UNSORTED = {
    "interview": [
        # normal options
        "success",      # 'year', 'rural' potentially as well

        # non uni specific
        "preference", 
        
        # uni specific
        "casper quartile", "deakin bonus", "anu bonus", "mq bonus", 'unimelb gam', 
        'undf bonuses', 'unds bonuses', 'uow bonuses'
    ],
    "offer": [
        # normal options
        "success", 'offer uni place type',     # 'year', 'rural' potentially as well

        # non specifc unis stuff
        "preference", 'interviewed?', 'interview opinion', 'interview prep hours', #'places selected',
        
        # more uni specific
        'casper quartile', 'deakin bonus', 'anu bonus', 'mq bonus', 'uq rmp tier'
    ]
}

LEGEND_OPTIONS = {
    data_type: sorted(legend_options) for data_type, legend_options in LEGEND_OPTIONS_UNSORTED.items()
}

# for ensuring there is a correct ordering
ORDER_OVERIDE = {
    'interview opinion': ['Very well', 'Well', 'Unsure', 'Poorly', 'Very poorly'],
    'interviewed?': ['Yes', 'No', 'None'],
    'offer uni place type': ['CSP', 'BMP', 'FFP'],
    'deakin bonus': [str(x) for x in range(0, 21, 2)],
    #'places selected': ['CSP', 'BMP', 'FFP']
    'interview prep hours': ['250+', '101-250', '51-100', '26-50', '11-25', '6-10', '0-5', 'None']
}