import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(layout="wide")

## SETTING UP DATA
# cache data
@st.cache_data
def load_csv(file_path):
    return pd.read_csv(file_path)
# read in data
house = load_csv('data/house_finances_gender.csv')
# title case candidate names
house["Candidate"] = house["Candidate"].str.title()
# rename columns
house.rename(columns={'Contributions  from Individuals': 'From Individuals', 
                      'Contributions and Loans from   the Candidate': 'From Candidate',
                      'Contributions from PACs and Other Committees': 'From PACs and Committees',
                      'Incumbent/ Challenger/Open': 'Incumbent/Challenger/Open',
                      'Elected?' : 'Elected_bool',
                      'Elected?1': 'Elected?',
                      'sum receipts': 'Sum Receipts'}, inplace=True)
# remove leading spaces from gender column
house['Gender'] = house['Gender'].str.strip()
# remove mr, ms, mrs, miss, and rep. from candidate names
house["Candidate"] = house["Candidate"].str.replace("Mr.", '')
house["Candidate"] = house["Candidate"].str.replace("Ms.", '')
house["Candidate"] = house["Candidate"].str.replace("Mrs.", '')
house["Candidate"] = house["Candidate"].str.replace("Miss.", '')
house["Candidate"] = house["Candidate"].str.replace("Rep.", '')
# split candidate name into last, first, and suffix
name_split = house['Candidate'].str.split(', ', expand=True, n=2)
house['last_name'] = name_split[0]
house['first_name'] = name_split[1]
house['suffix'] = name_split[2]
# put names together
house['Candidate'] = house['first_name'] + ' ' + house['last_name'] \
    + house['suffix'].apply(lambda x: ', ' + x if pd.notna(x) else '')
# drop columns
house.drop(['first_name', 'last_name', 'suffix'], axis=1, inplace=True)
## END SETTING UP DATA

st.markdown("<h1 style='text-align: center;'>2022 U.S. House of Representatives Campaign Fundraising by Gender</h1>", unsafe_allow_html=True)
st.write(" ")
st.markdown("""
    Historically, women running for the U.S. House of Representatives\
    have been at a disadvantage due to fundraising. However, in the 2018\
    and 2020 elections, women outraised men on average. [[1]](#sources)\
    This continued in 2022, with women running for the House raising an average \
    of \$1,011,166.89 and men raising an average of $768,222.34. This is a crucial\
    development, as the candidate who fundraises the most wins 90% of elections. [[2]](#sources) \
    Although women have been raising more in the past few elections, they are still\
    underrepresented in the House of Representatives.
""", unsafe_allow_html=True)
st.write("Out of the 2,311 candidates that ran for the U.S. House of Representatives\
        in 2022, 675 were women and 1636 were men.")
st.write("Out of the 435 elected representatives, 124 were women and 311 were men. So,\
        28.5% of the house is women.")
st.write("Out of 950 Democratic candidates, 38% were women. Out of 1,250 Republican\
        candidates, 22% were women.")

# filter for elected representatives
winners = house[house["Win?"] == 1]
# select a state
# add all states option
unique_states = sorted(["All States"] + list(house["State"].unique()))  
# make select box and make all states the default
selected_state = st.sidebar.selectbox("Select a state:", unique_states, index=2)
# filter data based on selected state
# all states
if selected_state == "All States":
    select_data = house.copy()
    select_data_win = winners.copy()
# if a state is selected
else:
    select_data = house[house["State"] == selected_state]
    select_data_win = winners[winners["State"] == selected_state]
    # get unique congressional districts for the selected state
    districts = sorted(list(select_data["District"].unique()))
    # add all districts at beginning of list
    districts.insert(0, "All Districts")
    # make selectbox to select a district
    selected_district = st.sidebar.selectbox("Select a Congressional District:", districts)
    # all districts
    if selected_district == "All Districts":
        select_data = select_data.copy()
        select_data_win = select_data_win.copy()
    # if a district is selected
    else:
        # filter data based on selected district
        select_data = select_data[select_data["District"] == selected_district]
        select_data_win = select_data_win[select_data_win["District"] == selected_district]
        # find winner of district
        winner = " "  # if no winner found
        winning_candidate = select_data[select_data["Win?"] == 1]
        if not winning_candidate.empty:
            winner = winning_candidate.iloc[0]["Candidate"]
            winner_party = winning_candidate.iloc[0]["Party"]
        st.sidebar.write("Elected Candidate:", winner, ", ", winner_party)

# group by party group and gender and get sum receipts for each group
party_gender_receipts = select_data.groupby(['Party Group', 'Gender'])['Sum Receipts'].sum().reset_index()
party_gender_receipts_win = select_data_win.groupby(['Party Group', 'Gender'])['Sum Receipts'].sum().reset_index()
# group by party group and gender and get count for each group
party_gender_only = select_data.groupby(['Party Group', 'Gender']).size().reset_index()
party_gender_only_win = select_data_win.groupby(['Party Group', 'Gender']).size().reset_index()
# merge the two
party_gender = party_gender_receipts.merge(party_gender_only, on=['Party Group', 'Gender'])
party_gender_win = party_gender_receipts_win.merge(party_gender_only_win, on=['Party Group', 'Gender'])
# rename the number of candidates column
party_gender.rename(columns={0: 'Number of Candidates'}, inplace=True)
party_gender_win.rename(columns={0: 'Number of Candidates'}, inplace=True)
# change from female and male to women and men
party_gender["Gender"] = party_gender["Gender"].str.replace("Female", 'Women')
party_gender["Gender"] = party_gender["Gender"].str.replace("Male", 'Men')
party_gender_win["Gender"] = party_gender_win["Gender"].str.replace("Female", 'Women')
party_gender_win["Gender"] = party_gender_win["Gender"].str.replace("Male", 'Men')

# for displaying number of candidates in each category
# pivot and find sum of the number of candidates in each category
pivot_df = party_gender.pivot_table(index='Party Group', columns='Gender', values='Number of Candidates', aggfunc='sum', fill_value=0)
pivot_df_win = party_gender_win.pivot_table(index='Party Group', columns='Gender', values='Number of Candidates', aggfunc='sum', fill_value=0)
# merge the pivot with the original dataframe on party group
candidates_group = party_gender.merge(pivot_df, on='Party Group')
candidates_group_win = party_gender_win.merge(pivot_df_win, on='Party Group')
# rename columns
candidates_group.rename(columns={'female': 'female_candidates', 'male': 'male_candidates'}, inplace=True)
candidates_group_win.rename(columns={'female': 'female_candidates', 'male': 'male_candidates'}, inplace=True)
# drop unnecessary columns
candidates_group.drop(columns=['Number of Candidates', "Gender", "Sum Receipts"], inplace=True)
candidates_group_win.drop(columns=['Number of Candidates', "Gender", "Sum Receipts"], inplace=True)
# drop duplicate columns
candidates_group.drop_duplicates(inplace=True)
candidates_group_win.drop_duplicates(inplace=True)
# fill nan values with 0
candidates_group.fillna(0, inplace=True)
candidates_group_win.fillna(0, inplace=True)
# reset index
candidates_group = candidates_group.reset_index(drop=True)
candidates_group_win = candidates_group_win.reset_index(drop=True)

# extract number of candidates in each category
try:
    # make sure dataframe is lining up properly
    if candidates_group.at[0, 'Party Group'] == "Democratic Party":
        dw = candidates_group.at[0, 'Women']
    else:
        dw = 0
# if there are no candidates in this category 
except KeyError:
    dw = 0 
try:
    # if selected state/district has no democratic candidates, row 0 will  
    # be republican party, so check for that
    if candidates_group.at[0, 'Party Group'] == "Republican Party":
        rw = candidates_group.at[0, 'Women']
    elif candidates_group.at[1, 'Party Group'] == "Republican Party":
        rw = candidates_group.at[1, 'Women']
    else:
        rw = 0
except KeyError:
    rw = 0 
try:
    if candidates_group.at[0, 'Party Group'] == "Democratic Party":
        dm = candidates_group.at[0, 'Men'] 
    else:
        dm = 0
except KeyError:
    dm = 0 
try:
    if candidates_group.at[0, 'Party Group'] == "Republican Party":
       rm = candidates_group.at[0, 'Men']  
    elif candidates_group.at[1, 'Party Group'] == "Republican Party":
        rm = candidates_group.at[1, 'Men']
    else:
        rm = 0 
except KeyError:
    rm = 0 
st.markdown("""<h4 id="Candidates" style='text-align: center;'>Number of Candidates</h4> """, unsafe_allow_html=True)
# columns to show values in a table
col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
with col3:
    # blank space to make values line up correctly
    st.write("&nbsp;")
    st.markdown("Women:")
    st.markdown("Men:")
with col4:
    st.write("Democrats")
    st.markdown(f"**{dw}**")
    st.markdown(f"**{dm}**")
with col5:
    st.write("Republicans")
    st.markdown(f"**{rw}**")
    st.markdown(f"**{rm}**")

# specify colors for charts
colors = alt.Scale(domain = ['Democratic Party', 'Republican Party', 'Third Party'], range=  ['blue', 'red', 'gray'])

# bar chart for all candidates
gender_split = alt.Chart(party_gender).mark_bar().encode(
    x = alt.X('Gender:N', axis = alt.Axis(title = None, labelAngle = 0)),
    y = alt.Y('Sum Receipts:Q', axis = alt.Axis(title = 'Sum Receipts ($)')),
    column = alt.Column('Party Group:N', title = "Campaign Receipts by Party and Gender"),
    color = alt.Color('Party Group:N', scale = colors),
    tooltip = ['Number of Candidates', 'Sum Receipts']
).properties(
    width = 115 
)

# bar chart for elected representatives
gender_split_win = alt.Chart(party_gender_win).mark_bar().encode(
x = alt.X('Gender:N', axis = alt.Axis(title = None, labelAngle = 0)),
y = alt.Y('Sum Receipts:Q', axis = alt.Axis(title = 'Sum Receipts ($)')),
column = alt.Column('Party Group:N', title = "Campaign Receipts by Party and Gender"),
color = alt.Color('Party Group:N', scale = colors),
tooltip = ['Number of Candidates', 'Sum Receipts']
).properties(
    width = 115 
)

tab1, tab2 = st.tabs(["All Candidates", "Elected Candidates"])
with tab1:
    st.altair_chart(gender_split)
with tab2:
    st.altair_chart(gender_split_win)

# group by party group and gender and get category totals for each group
# for all
party_gender_pacs = select_data.groupby(['Party Group', 'Gender'])['From PACs and Committees'].sum().reset_index()
party_gender_ind = select_data.groupby(['Party Group', 'Gender'])['From Individuals'].sum().reset_index()
party_gender_cand = select_data.groupby(['Party Group', 'Gender'])['From Candidate'].sum().reset_index()
# for elected candidates
party_gender_pacs_win = select_data_win.groupby(['Party Group', 'Gender'])['From PACs and Committees'].sum().reset_index()
party_gender_ind_win = select_data_win.groupby(['Party Group', 'Gender'])['From Individuals'].sum().reset_index()
party_gender_cand_win = select_data_win.groupby(['Party Group', 'Gender'])['From Candidate'].sum().reset_index()
# group by party group and gender and get count for each group
# for all
party_gender_only = select_data.groupby(['Party Group', 'Gender']).size().reset_index()
# for elected candidates
party_gender_only_win = select_data_win.groupby(['Party Group', 'Gender']).size().reset_index()
# merge the two
# for all
ind_pacs = party_gender_pacs.merge(party_gender_ind, on=['Party Group', 'Gender'])
party_gender_receipts_cat = ind_pacs.merge(party_gender_cand, on = ['Party Group', 'Gender'])
party_gender = party_gender_receipts_cat.merge(party_gender_only, on = ['Party Group', 'Gender'])
# for elected
ind_pacs_win= party_gender_pacs_win.merge(party_gender_ind_win, on = ['Party Group', 'Gender'])
party_gender_receipts_cat_win = ind_pacs_win.merge(party_gender_cand_win, on = ['Party Group', 'Gender'])
party_gender_win = party_gender_receipts_cat_win.merge(party_gender_only_win, on = ['Party Group', 'Gender'])
# rename the number of candidates column
party_gender.rename(columns = {0: 'Number of Candidates'}, inplace = True)
party_gender_win.rename(columns = {0: 'Number of Candidates'}, inplace = True)
# change from female and male to women and men
# for all
party_gender["Gender"] = party_gender["Gender"].str.replace("Female", 'Women')
party_gender["Gender"] = party_gender["Gender"].str.replace("Male", 'Men')
# for elected candidates
party_gender_win["Gender"] = party_gender_win["Gender"].str.replace("Female", 'Women')
party_gender_win["Gender"] = party_gender_win["Gender"].str.replace("Male", 'Men')
# split based on party
dem = party_gender[party_gender['Party Group'] == 'Democratic Party']
rep = party_gender[party_gender['Party Group'] == 'Republican Party']
dem_win = party_gender_win[party_gender_win['Party Group'] == 'Democratic Party']
rep_win = party_gender_win[party_gender_win['Party Group'] == 'Republican Party']

# find max value for charts
if max(dem['From Individuals'].max(), rep['From Individuals'].max()) > 0:
    max_amount1 = max(dem['From Individuals'].max(), rep['From Individuals'].max())
    max_amount2 = max(dem['From PACs and Committees'].max(), rep['From PACs and Committees'].max())
    max_amount = max(max_amount1, max_amount2)
else:
    try:
        max_amount1 = dem.at[0, 'From Individuals']
        max_amount2 = dem.at[0, 'From PACs and Committees']
        max_amount = max(max_amount1, max_amount2) 
    except KeyError:
        max_amount1 = rep.at[0, 'From Individuals']
        max_amount2 = rep.at[0, 'From PACs and Committees']
        max_amount = max(max_amount1, max_amount2) 
if max(dem_win['From Individuals'].max(), rep_win['From Individuals'].max()) > 0:
    max_amount_win1 = max(dem_win['From Individuals'].max(), rep_win['From Individuals'].max())
    max_amount_win2 = max(dem_win['From PACs and Committees'].max(), rep_win['From PACs and Committees'].max())
    max_amount_win = max(max_amount_win1, max_amount_win2)
else:
    try:
        max_amount_win1 = dem_win.at[0, 'From Individuals']
        max_amount_win2 = dem_win.at[0, 'From PACs and Committees']
        max_amount_win = max(max_amount_win1, max_amount_win2)
    except KeyError:
        max_amount_win1 = rep_win.at[0, 'From Individuals']
        max_amount_win2 = rep_win.at[0, 'From PACs and Committees']
        max_amount_win = max(max_amount_win1, max_amount_win2)
# democratic candidates
categories_dem = alt.Chart(dem).mark_bar().encode(
    x = alt.X('Category:N', axis=alt.Axis(title = None)),
    y = alt.Y('Amount ($):Q', scale=alt.Scale(domain = (0, max_amount))),
    column = alt.Column('Gender:N', title = "Democratic Party"),
    color = alt.Color('Party Group:N', scale = colors),
    tooltip = ['Number of Candidates', 'Amount ($):Q']
).transform_fold(
    as_ = ['Category', 'Amount ($)'],
    fold = ['From Individuals', 'From PACs and Committees', 'From Candidate']
).properties(
    width = 115
).configure_legend(
    disable = True
)
# republican candidates
categories_rep = alt.Chart(rep).mark_bar().encode(
    x = alt.X('Category:N', axis = alt.Axis(title = None)),
    y = alt.Y('Amount ($):Q', scale = alt.Scale(domain = (0, max_amount))),
    column = alt.Column('Gender:N', title = "Republican Party"),
    color = alt.Color('Party Group:N', scale = colors),
    tooltip = ['Number of Candidates', 'Amount ($):Q']
).transform_fold(
    as_ = ['Category', 'Amount ($)'],
    fold = ['From Individuals', 'From PACs and Committees', 'From Candidate']
).properties(
    width = 115
).configure_legend(
    disable = True
)
# elected democrats
categories_dem_win = alt.Chart(dem_win).mark_bar().encode(
    x = alt.X('Category:N', axis = alt.Axis(title = None)),
    y = alt.Y('Amount ($):Q', scale = alt.Scale(domain = (0, max_amount_win))),
    column = alt.Column('Gender:N', title = "Democratic Party"),
    color = alt.Color('Party Group:N', scale = colors),
    tooltip = ['Number of Candidates', 'Amount ($):Q']
).transform_fold(
    as_ = ['Category', 'Amount ($)'],
    fold = ['From Individuals', 'From PACs and Committees', 'From Candidate']
).properties(
    width = 115
).configure_legend(
    disable=True
)
# elected republicans
categories_rep_win = alt.Chart(rep_win).mark_bar().encode(
    x = alt.X('Category:N', axis = alt.Axis(title = None)),
    y = alt.Y('Amount ($):Q', scale = alt.Scale(domain = (0, max_amount_win))),
    column = alt.Column('Gender:N', title = "Republican Party"),
    color = alt.Color('Party Group:N', scale = colors),
    tooltip = ['Number of Candidates', 'Amount ($):Q']
).transform_fold(
    as_ = ['Category', 'Amount ($)'],
    fold = ['From Individuals', 'From PACs and Committees', 'From Candidate']
).properties(
    width = 115
).configure_legend(
    disable=True
)

st.write("While women raised more on average overall, in the 2022 House election,\
        it was in different categories. Even though there are several PACs dedicated\
         to electing women into office, PACs generally donate more to men than they\
         do to women. This may be because PACs tend to donate to incumbent candidates,\
         a group which is mostly men. [[1]](#sources)")
st.write("Additionally, Democratic women tend to receive more money from PACs than\
         Republican women. This may be because there are much fewer incumbent Republican\
         women than incumbent Democratic women. [[1]](#sources) Also, most of the PACs focused on women\
         donate to Democratic candidates. [[3]](#sources)")

tab1, tab2 = st.tabs(["All Candidates", "Elected Candidates"])
with tab1:
    st.markdown("<p style='text-align: center;'>Campaign Receipts by Contribution\
                 Category</p>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.altair_chart(categories_dem)
    with col2:
        st.altair_chart(categories_rep)
with tab2:
    st.markdown("<p style='text-align: center;'>Campaign Receipts by Contribution\
                 Category</p>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.altair_chart(categories_dem_win)
    with col2:
        st.altair_chart(categories_rep_win)

st.markdown("""
    <h4 id="Source1">Sources</h4>
    <p>[1] <a href = "https://www.theascendfund.org/post/cost-of-success-political-fundraising-as-a-barrier-to-equity#viewer-4rgb0">
        The Ascend Fund: Cost of Success – Political Fundraising as a Barrier to Equity</a></p>
    <p>[2] <a href = "https://fivethirtyeight.com/features/money-and-elections-a-complicated-love-story/">
        FiveThirtyEight: How Money Affects Elections</a></p>
    <p>[3] <a href = "https://www.pgpf.org/sites/default/files/US-2050-Race-Gender-and-Money-in-Politics-Campaign-Finance-and-Federal-Candidates-in-the-2018-Midterms.pdf">
        Race, Gender, and Money in Politics: Campaign Finance and Federal Candidates in the
        2018 Midterms</a></p>
    <p>Data: <a href = "https://www.fec.gov/campaign-finance-data/congressional-candidate-data-summary-tables/?year=2022&segment=12">
        Federal Election Commission</a></p>
""", unsafe_allow_html=True)