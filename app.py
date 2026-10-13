"""
========================
Welcome page for the app
========================

Author: github.com/cyrilby
Last meaningful update: 13-10-2026
"""

# %% Setting up

import streamlit as st
import yaml

from helpers import check_missing_mapping, get_latest_status, get_unique_days
from interface import add_logo, add_sidebar, apply_theme, customize_colors
from storage import connect_to_db, download_s3_file

# Applying the app's overall theme
apply_theme()

# Adding a sidebar
add_sidebar()

# Importing long text strings used in the app
with open("text.yaml", "r", encoding="utf-8") as file:
    text = yaml.safe_load(file)


# Downloading the latest version of the DuckDB file
# and then creating a connection to the local database
@st.cache_resource
def fetch_app_data():
    with st.spinner("Getting latest data..."):
        download_s3_file("database.duckdb", "database.duckdb")


# Connecting to the locally synced DuckDB
with st.spinner("Getting latest data..."):
    fetch_app_data()

conn = connect_to_db()


# %% Page: Welcome to the app


# Informs the user of the app's purpose
customize_colors()
st.header("Welcome to the CPH metro status app!")
add_logo()
st.markdown(text["home_msg_1"])
st.markdown(text["home_msg_2"])
st.image(
    "resources/metro_map_with_stations.png"
)  # image can be disabled in development phase

# Fetching relevant bits of data
_, _, n_days, _ = get_unique_days()

# Displaying the latest service message from the metro's website
st.subheader("Latest service status data", divider="grey")
_, mapping_warning = check_missing_mapping()
if mapping_warning:
    st.warning(mapping_warning)

most_recent, last_update_date, last_update_time = get_latest_status()
msg_text = text["home_msg_3"]
msg_text = msg_text.format(
    last_update_date=last_update_date, last_update_time=last_update_time
)
st.markdown(msg_text)
st.dataframe(most_recent)

# Displaying more info on how the app can help the user
st.subheader("How this app can help you", divider="grey")
st.markdown(text["home_msg_4"])
msg_text = text["home_msg_5"]
msg_text = msg_text.format(n_days=n_days)
st.markdown(msg_text)

# Displaying more info on how to use the app
st.subheader("How to use this app", divider="grey")
st.markdown("This app consists of the following two panes:")
st.markdown(text["home_msg_6"])
# st.markdown(
#     "To **switch between different pages**, please click on the page title:"
# )
st.image("resources/pages_examples.PNG")
st.markdown("You will then be redirected to the desired page.")

# Displaying more info on how the user can filter the data
st.subheader("How to apply filters to the data", divider="grey")
st.markdown(text["home_msg_7"])
st.image("resources/filter_date.PNG")
st.markdown(text["home_msg_8"])
st.image("resources/filter_lines.PNG")
st.markdown(text["home_msg_9"])
st.image("resources/selection_warning.PNG")
st.markdown(text["home_msg_10"])
st.divider()
st.markdown("*Front page image source: Metroselskabet (www.m.dk)*")


# %%
