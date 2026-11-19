"""
============================
Methodology information page
============================

Author: github.com/cyrilby
Last meaningful update: 19-11-2026
"""

# %% Setting up

import streamlit as st

from core.helpers import load_text
from core.storage import get_app_data

# Importing data and text strings used in the app
text = load_text()
conn = get_app_data()


# %% Specific page content

# Loading additional data for this page
query = "SELECT * FROM mapping_messages"
mapping_messages = conn.execute(query).fetch_df()
query = "SELECT * FROM mapping_downtime"
system_downtime = conn.execute(query).fetch_df()

# Building the page's layout
st.header("Information on data collection & processing")
st.markdown(text["meth_page_desc"])
st.subheader("Sourcing operational data", divider="grey")
st.markdown(text["meth_msg_1"])
st.markdown(text["meth_msg_2"])

st.subheader("Interpreting status messages", divider="grey")
st.markdown(text["meth_msg_3"])
st.markdown(text["meth_msg_4"])
st.dataframe(mapping_messages)

st.subheader("Dealing with system downtime", divider="grey")
st.markdown(text["meth_msg_5"])
st.image("resources/filter_downtime.PNG")

st.markdown(text["meth_msg_6"])
system_downtime = system_downtime.sort_values("date", ascending=False)
st.dataframe(system_downtime)

# %%
