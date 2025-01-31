import pandas as pd
import numpy as np

from . import parameters

# ------------------------- Filtering Functions -----------------------------------------


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
    df_filtered.loc[:, 'combo'] = (df_filtered['gamsat'] / 100) + (df_filtered['gpa'] / 7)

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
    df_filtered.loc[:, 'combo'] = (df_filtered['gamsat'] / 100) + (df_filtered['gpa'] / 7)

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
    
    
