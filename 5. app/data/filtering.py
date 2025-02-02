import pandas as pd
import numpy as np

from . import parameters

# column names
GAMSAT = 'gamsat'
GPA = 'gpa'
COMBO = 'combo'
SCALED_COMBO = 'scaled combo'

# uni names
ANU = 'Australian National University'
DEAKIN = 'Deakin University'
MACQUARIE = 'Macquarie University'
ND_FREMANTLE = 'The University of Notre Dame Fremantle'
ND_SYDNEY = 'The University of Notre Dame Sydney'

# get the scaled unis and ones to handle carefully
SCALED_UNIS = [ANU, DEAKIN, MACQUARIE, ND_FREMANTLE, ND_SYDNEY]
ND_UNIS = [ND_FREMANTLE, ND_SYDNEY]

DO_ND_SCALING = False

# ------------------------- Filtering Functions -----------------------------------------


# convert combo score to scaled combo score
# Does as Much scaling as possible
# NO ND SCALING NO ND SCALING NO ND SCALING NO ND SCALING NO ND SCALING NO ND SCALING NO ND SCALING
def get_scaled_combo(uni_dataset, uni_name, interview=True):
    # ANU
    if (uni_name == ANU):
        uni_dataset.loc[:, SCALED_COMBO] = uni_dataset.loc[:, COMBO] * (1 + uni_dataset.loc[:, 'anu bonus'].astype(int) / 100)
    
    # Deakin
    elif (uni_name == DEAKIN):
        uni_dataset.loc[:, SCALED_COMBO] = uni_dataset.loc[:, COMBO] * (1 + uni_dataset.loc[:, 'deakin bonus'].astype(int) / 100)
    
    # MACQUARIE (not accounting for interview)
    elif (uni_name == MACQUARIE):
        uni_dataset.loc[:, SCALED_COMBO] = (
            (uni_dataset.loc[:, GAMSAT] / 100) + (uni_dataset.loc[:, GPA] / 7) * (1 + uni_dataset.loc[:, 'mq bonus'].astype(int) / 100)
        )
    
    # ND_UNIS (don't change offer data as don't have the data)
    elif (uni_name in ND_UNIS and interview and DO_ND_SCALING):
        # apply combo as normal
        uni_dataset.loc[:, SCALED_COMBO] = uni_dataset.loc[:, COMBO]

        # find location 2024 interview and get the bonus column
        year_2024_mask = uni_dataset['year'] == 2024
        bonus_column = "undf bonuses" if uni_name == ND_FREMANTLE else "unds bonuses"

        # apply the transform
        uni_dataset.loc[year_2024_mask, SCALED_COMBO] = (
            (6 * uni_dataset.loc[year_2024_mask, SCALED_COMBO] / 2 + 
            uni_dataset.loc[year_2024_mask, bonus_column] / 100) / 7
        )
    else:
        uni_dataset.loc[:, SCALED_COMBO] = uni_dataset.loc[:, COMBO]
    
    return uni_dataset


# na values should be:
# - preference of unis
# - That's it
def filter_uni_interview(df, uni_name):
    # Filter for rows where the university appears in interview or preferences columns
    df_filtered = df[
        (df['interview uni'] == uni_name) |
        (df['pref 1 uni'] == uni_name) |
        (df['pref 2 uni'] == uni_name) |
        (df['pref 3 uni'] == uni_name) |
        (df['pref 4 uni'] == uni_name) |
        (df['pref 5 uni'] == uni_name) |
        (df['pref 6 uni'] == uni_name)
    ].copy()
    
    # Define the success column
    df_filtered['success'] = np.where(df_filtered['interview uni'] == uni_name, 'Yes', 'No')
    
    # Calculate the preference number based on success
    df_filtered['preference'] = np.where(
        df_filtered['success'] == 'Yes',
        df_filtered[['pref 1 uni', 'pref 2 uni', 'pref 3 uni', 'pref 4 uni', 'pref 5 uni', 'pref 6 uni']].notna().sum(axis=1) + 1,
        np.select(
            [
                df_filtered['pref 1 uni'] == uni_name,
                df_filtered['pref 2 uni'] == uni_name,
                df_filtered['pref 3 uni'] == uni_name,
                df_filtered['pref 4 uni'] == uni_name,
                df_filtered['pref 5 uni'] == uni_name,
                df_filtered['pref 6 uni'] == uni_name
            ],
            ['1', '2', '3', '4', '5', '6'],
            default='None'
        )
    )
    
    # Select the appropriate gamsat and gpa based on where the uni appears
    df_filtered['gamsat'] = np.where(
        df_filtered['success'] == 'Yes',
        df_filtered['interview uni gamsat'],
        np.select(
            [
                df_filtered['pref 1 uni'] == uni_name,
                df_filtered['pref 2 uni'] == uni_name,
                df_filtered['pref 3 uni'] == uni_name,
                df_filtered['pref 4 uni'] == uni_name,
                df_filtered['pref 5 uni'] == uni_name,
                df_filtered['pref 6 uni'] == uni_name
            ],
            [
                df_filtered['pref 1 gamsat'],
                df_filtered['pref 2 gamsat'],
                df_filtered['pref 3 gamsat'],
                df_filtered['pref 4 gamsat'],
                df_filtered['pref 5 gamsat'],
                df_filtered['pref 6 gamsat']
            ],
            default=np.nan
        )
    )

    # Likewise for gpa
    df_filtered['gpa'] = np.where(
        df_filtered['success'] == 'Yes',
        df_filtered['interview uni gpa'],
        np.select(
            [
                df_filtered['pref 1 uni'] == uni_name,
                df_filtered['pref 2 uni'] == uni_name,
                df_filtered['pref 3 uni'] == uni_name,
                df_filtered['pref 4 uni'] == uni_name,
                df_filtered['pref 5 uni'] == uni_name,
                df_filtered['pref 6 uni'] == uni_name
            ],
            [
                df_filtered['pref 1 gpa'],
                df_filtered['pref 2 gpa'],
                df_filtered['pref 3 gpa'],
                df_filtered['pref 4 gpa'],
                df_filtered['pref 5 gpa'],
                df_filtered['pref 6 gpa']
            ],
            default=np.nan
        )
    )

    # sanity check below (ALL GOOD)
    #print(((df_filtered[["gamsat", "gpa"]].isna().any(axis=1)) & (df_filtered[["gamsat", "gpa"]].notna().any(axis=1))).sum())

    # add the combo score
    df_filtered.loc[:, COMBO] = (df_filtered['gamsat'] / 100) + (df_filtered['gpa'] / 7)

    # get the scaled combo score
    df_filtered = get_scaled_combo(df_filtered, uni_name, interview=True)

    # convert the values
    df_filtered.index.name = 'index'

    return df_filtered


# note: this function will search for where the uni name is equal to the uni name provided, nothing else
  # but it will also use notna() function for both the 'offer uni place type' and 'interview uni'
def filter_uni_offer(df, uni_name):
    # Filter for rows where the university appears in either offer or interview columns
    df_filtered = df[
        (df['offer uni'] == uni_name) |
        (df['interview uni'] == uni_name)
    ].copy()
    
    # Define the success column based on whether the uni appears in the offer column
    df_filtered['success'] = np.where(df_filtered['offer uni'] == uni_name, 'Yes', 'No')
    
    # Define preference based on the year of preference for offer or interview uni preference
    df_filtered['preference'] = np.where(
        df_filtered['success'] == 'Yes',
        df_filtered['offer uni preference'],
        df_filtered['interview uni preference']
    )
    
    # Select the appropriate gamsat score based on where the uni appears (offer or interview)
    df_filtered['gamsat'] = np.where(
        df_filtered['success'] == 'Yes',
        df_filtered['offer uni gamsat'],
        df_filtered['interview uni gamsat']
    )

    # Select the appropriate gpa based on where the uni appears (offer or interview)
    df_filtered['gpa'] = np.where(
        df_filtered['success'] == 'Yes',
        df_filtered['offer uni gpa'],
        df_filtered['interview uni gpa']
    )

    # Define type: if 'offer uni place type' is not NaN, take its value; otherwise, take 'places selected'
    df_filtered['type'] = np.where(
        df_filtered['offer uni place type'].notna(),
        df_filtered['offer uni place type'],
        df_filtered['places selected']
    )

    df_filtered['interview uni'] = np.where(
        df_filtered['interview uni'].notna(),
        df_filtered['interview uni'],
        df_filtered['offer uni']
    )

    # sanity check below (ALL GOOD)
    #print(((df_filtered[["gamsat", "gpa"]].isna().any(axis=1)) & (df_filtered[["gamsat", "gpa"]].notna().any(axis=1))).sum())
    df_filtered['interviewed?'] = np.where(
        df_filtered['success'] == 'Yes',
        df_filtered['interviewed?'],
        'None'
    )

    # add the combo score
    df_filtered.loc[:, COMBO] = (df_filtered['gamsat'] / 100) + (df_filtered['gpa'] / 7)

    # add the scaled combo score
    df_filtered = get_scaled_combo(df_filtered, uni_name, interview=True)    

    df_filtered.index.name = 'index'

    return df_filtered


# -------------------------------- Create Dictionaries ---------------------------------


def create_options(interview_df, offer_df):
    uni_options = {}

    # INTERVIEW DATA
    # get the options for the interview data
    interview_unis = set(interview_df["interview uni"].unique())
    for pref_num in range(1, 7):
        interview_unis = interview_unis | set(interview_df[f"pref {pref_num} uni"].unique())
    
    # remove the NANs from the data
    uni_options["interview"] = sorted([x for x in interview_unis if pd.notna(x)])

    
    # OFFER DATA
    # get the options for offer data
    offer_unis = set(offer_df["offer uni"]) | set(offer_df["interview uni"])
    
    # remove NANs from data and add to dictionary
    uni_options["offer"] = sorted([x for x in offer_unis if pd.notna(x)])

    return uni_options


def create_filters(interview_df, offer_df):
    uni_filters = {"interview": {}, "offer": {}}

    # get the options
    uni_options = create_options(interview_df, offer_df)

    # INTERVIEW DATA
    # get each uni and filter
    for uni in uni_options["interview"]:
        uni_filters["interview"][uni] = filter_uni_interview(interview_df, uni)

    # OFFER DATA
    # get each uni and filter
    for uni in uni_options["offer"]:
        uni_filters["offer"][uni] = filter_uni_offer(offer_df, uni)

    return uni_filters
    
    
