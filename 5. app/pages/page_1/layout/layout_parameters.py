# ---------------------------- FILTERING ----------------------------------------------------

# display variables
PLACEHOLDER = "select"
SINGLE_OPTION_FILTERS = ['university', 'year']
START_BLANK = ['places selected (include all)', 'places selected (exclude all)']

# used for changing the display name of a filter
filter_to_title = {}

# ----------------------------- GRAPHING ----------------------------------------------------

# a really important term for filtering
SUCCESS = 'success'

DEFAULT_TITLES = {
    'scatter': 'GAMSAT vs GPA',
    'histogram': 'Combo Score Frequency'
}

DEFAULT_LEGEND = SUCCESS

GAMSAT_LIM = [55, 85]
GPA_LIM = [5.2, 7.2]

OPACITY = 0.7

# for the legend aspect
#COLOUR_DISCRETE_MAP = {'Yes': 'blue', 'No': 'red'}
#CATEGORY_ORDERS = {SUCCESS: ['Yes', 'No']}
