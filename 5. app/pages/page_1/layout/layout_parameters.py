import numpy as np

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

# get the place holder and default option
LEGEND_PLACE_HOLDER = 'Choose A Legend'
LEGEND_DEFAULT_OPTION = SUCCESS

# the name of the place holder
GRAPH_PLACEHOLDER = 'Choose A Graph Type'

# naming the graph components
GAMSAT_VS_GPA_GRAPH = 'GAMSAT vs GPA'
COMBO_SCORE_GRAPH = 'Combo Score'
COMBO_SCORE_SCALED_GRAPH = 'Combo Score Scaled'

# get the graph options and default value
GRAPH_OPTIONS = [
    GAMSAT_VS_GPA_GRAPH,
    COMBO_SCORE_GRAPH,
    COMBO_SCORE_SCALED_GRAPH
]
GRAPH_DEFAULT_OPTION = GAMSAT_VS_GPA_GRAPH

DEFAULT_TITLES = {
    GAMSAT_VS_GPA_GRAPH: 'GAMSAT vs GPA',
    COMBO_SCORE_GRAPH: 'Combo Score Frequency',
    COMBO_SCORE_SCALED_GRAPH: 'Scaled Combo Score Frequency'
}

# -------- SCATTER ------------------

GAMSAT_LIM = [55, 85]
GPA_LIM = [5.2, 7.2]

OPACITY = 0.7

# -------- HISTOGRAM ----------------

# default ranges
X_RANGE = [1.54, 1.86]
BIN_HEIGHT = 60
MAX_HEIGHT_EXPAND = 1.1

# binning parameters
BIN_START = 1.2     # min is 1.22
BIN_END = 2         # max is 1.89
BIN_SIZE = 0.02

# binning implementation
EPSILON = 1e-12
COMBO_BINS = {
    'start': BIN_START - EPSILON,             
    'end': BIN_END - EPSILON,                 
    'size': BIN_SIZE
}
COMBO_BINS_NUMPY = np.arange(
    BIN_START - EPSILON,
    BIN_END + BIN_SIZE - EPSILON,
    BIN_SIZE
)