"""
======================
Legal information page
======================

Author: github.com/cyrilby
Last meaningful update: 19-11-2026
"""

# %% Setting up

import streamlit as st

from core.helpers import load_text

# Importing data and text strings used in the app
text = load_text()


# %% Specific page content

st.header("Legal disclaimer")
st.markdown(text["legal_disclaimer"])


# %%
