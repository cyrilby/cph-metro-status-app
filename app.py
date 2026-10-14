"""
========================
General interface set-up
========================

Author: github.com/cyrilby
Last meaningful update: 14-10-2026
"""

# %% Setting up

import streamlit as st

from core.interface import add_logo, apply_theme, customize_colors

# %% Launching the app

# Configure interface elements
add_logo()
apply_theme()
customize_colors()

st.set_page_config(page_title="CPH metro status", page_icon="🚇")

# Configure pages
pages = [
    st.Page("pages/homepage.py", title="Welcome"),
    st.Page("pages/overview.py", title="Overview"),
    st.Page("pages/daily_reliability.py", title="Daily reliability"),
]

pg = st.navigation(pages)
pg.run()


# %%
