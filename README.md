# 2022 House Campaign Finances by Gender
## Streamlit Application Link
[Link to Streamlit App](https://house-campaign-by-gender.streamlit.app/)

## Introduction
I wanted to explore the campaign fundraising patterns of political parties in the 2022 U.S. House of Representatives. I also wanted to explore the gender gap in fundraising.
This app shows the number of women and men running in each party, a bar chart with campaign receipts by party and gender, and the contributions by category by party and gender. All of this can be filtered by state and district.

## Data/operation abstraction design
I got my data from the [Federal Election Commission](https://www.fec.gov/campaign-finance-data/congressional-candidate-data-summary-tables/?year=2022&segment=12). I used ChatGPT to get the gender of most of the candidates. For the ones that ChatGPT missed, I used the individual candidate's website. I also added a column that indicated if the candidate won their election. I got this data from the [House of Representatives website](https://www.house.gov/representatives) and [Ballotpedia](https://ballotpedia.org/Main_Page). I did another [visalization](https://github.com/kpdavis2/2022-House-Campaign-Finances) with this data in Tableau, and downloaded that data to use for this project. In Tableau, I created boolean and Yes/No variables indicating if a candidate was elected. I also created the "sum receipts" variable and the "Party Group" variable, which grouped all third parties together. 

In Python I title-cased the candidate's names, put their names in "First Name Last Name" format, and dropped courtesy titles. I also renamed some of the columns to be more useful for the visualizations.

## Future work:
I think it would be interesting to explore the gender gap in political donors. This may correlate with the gender gap in fundraising.
