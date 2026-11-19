"""
==========================
Disruption calculator page
==========================

Author: github.com/cyrilby
Last meaningful update: 18-11-2026

==========================
WIP notes from 18-11-2026:
==========================
I've just copy-pasted the old page in here but I want to make
the page a bit more interactive and add charts for when the
station is most likely to be disrupted. This may require that
I pre-compute the disruption by station, day and hour for all
rows and then do the filtering in the page. But for now, at
least all pages of the old app are working as before 😉

--> I may even move this to the data scraper/cleaner workflow
so that I don't need to compute things in the app!
"""

# %% Setting up

import numpy as np
import streamlit as st

from core.helpers import load_text
from core.loader import get_filtered_data_calc, set_page_filters_calc
from core.storage import get_app_data

# Importing data and text strings used in the app
text = load_text()
conn = get_app_data()


# %% Common for all data-driven pages

# Page title displayed on top
st.header("Disruption calculator")

# Source & filter data, deal with warnings, etc.
page_filters = set_page_filters_calc()
data = get_filtered_data_calc(conn, page_filters)

min_date = data.min_date
max_date = data.max_date
n_days = data.n_days
selected_period = data.selected_period
selected_station = data.selected_station
selected_travel_day = data.selected_travel_day
selected_travel_time = data.selected_travel_time
df = data.df

# Confirming the selected period
# Note: we don't work with downtime period filtering on this page
st.sidebar.markdown(
    f"**Note:** this selection covers the period between {selected_period}."
)

# %% Specific page content [WIP as of 18-11-2026]

# Aggregating the data by day, hour and station
specific_impact = df.copy()
specific_impact["disruption"] = specific_impact["status_en_short"] == "Disruption"
specific_impact["total_rows"] = specific_impact.groupby(["station"])[
    "status_dk"
].transform("count")
specific_impact["disruption_rows"] = specific_impact.groupby(["station"])[
    "disruption"
].transform("sum")
specific_impact["disruption_chance_pct"] = np.round(
    100 * (specific_impact["disruption_rows"] / specific_impact["total_rows"]), 1
)
specific_impact = specific_impact.drop_duplicates(subset="station")

# Sorting the stations by the likelihood of disruptions
specific_impact = specific_impact.sort_values("disruption_chance_pct", ascending=False)
specific_impact = specific_impact.reset_index(drop=True)

# Exctracting info on the filtered time period
min_date = specific_impact["timestamp"].min().strftime("%d %B %Y")
max_date = specific_impact["timestamp"].max().strftime("%d %B %Y")

# Extracting key numbers to show as output
disruption_pct_selected = specific_impact[
    specific_impact["station"] == selected_station
]["disruption_chance_pct"].iloc[0]
disruption_pct_most = specific_impact[
    specific_impact["disruption_chance_pct"]
    == np.max(specific_impact["disruption_chance_pct"])
]["disruption_chance_pct"].iloc[0]
disruption_name_most = specific_impact[
    specific_impact["disruption_chance_pct"]
    == np.max(specific_impact["disruption_chance_pct"])
]["station"].iloc[0]
disruption_pct_least = specific_impact[
    specific_impact["disruption_chance_pct"]
    == np.min(specific_impact["disruption_chance_pct"])
]["disruption_chance_pct"].iloc[0]
disruption_name_least = specific_impact[
    specific_impact["disruption_chance_pct"]
    == np.min(specific_impact["disruption_chance_pct"])
]["station"].iloc[0]

# Printing the results to the user
st.subheader(f"Chances of disruption at {selected_station}", divider="grey")
calc_res_intro = text["calc_res_intro"]
calc_res_intro = calc_res_intro.format(min_date=min_date, max_date=max_date)
st.markdown(calc_res_intro)

calc_results = text["calc_results"]
calc_results = calc_results.format(
    selected_station=selected_station,
    selected_day=selected_travel_day,
    selected_hour=selected_travel_time,
    disruption_pct_selected=disruption_pct_selected,
    disruption_name_most=disruption_name_most,
    disruption_pct_most=disruption_pct_most,
    disruption_name_least=disruption_name_least,
    disruption_pct_least=disruption_pct_least,
)
st.markdown(calc_results)

# %%
