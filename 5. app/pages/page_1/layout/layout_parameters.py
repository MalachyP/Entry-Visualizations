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

# -------- SCATTER ------------------

GAMSAT_LIM = [55, 85]
GPA_LIM = [5.2, 7.2]

OPACITY = 0.7

# -------- HISTOGRAM ----------------

# default ranges
X_RANGE = [1.54, 1.86]
BIN_HEIGHT = 60
MAX_HEIGHT_EXPAND = 1.1

COMBO_BINS = {
    'start': 1.2,           # min is 1.22
    'end': 2,               # max is 1.89
    'size': 0.02
}
