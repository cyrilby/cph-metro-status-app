"""
============================================
Filters used by the various pages in the app
============================================

Author: github.com/cyrilby
Last meaningful update: 14-10-2026
"""

# %% Setting up

import datetime as dt

import pandas as pd
import streamlit as st

from core.helpers import load_text
from core.storage import get_app_data

conn = get_app_data()
text = load_text()

# %% Filter by date range


def filter_by_date_range(n_recent_days: int = 30):

    # Getting the first & last date in the data (to use for filtering)
    min_date_filter, max_date_filter = conn.execute(
        "SELECT MIN(date), MAX(date) FROM operation_fmt"
    ).fetchone()

    # Force compliance with pd datetime
    min_date_filter = pd.to_datetime(min_date_filter)
    max_date_filter = pd.to_datetime(max_date_filter)

    # Default date range: Last N recent days
    default_start = max_date_filter - dt.timedelta(days=n_recent_days)
    default_end = max_date_filter

    # Create a date input for start and end date
    selected_dates = st.sidebar.date_input(
        "Selected time period",
        (default_start, default_end),
        min_value=min_date_filter,
        max_value=max_date_filter,
        format="DD/MM/YYYY",
    )

    # If only 1 date is selected, we treat it as a start date
    # and set the end date to be N days later
    if len(selected_dates) == 0:
        start_date = default_start
        end_date = default_end
    elif len(selected_dates) == 1:
        start_date = selected_dates[0]
        end_date = start_date + dt.timedelta(days=n_recent_days)
    else:
        start_date = selected_dates[0]
        end_date = selected_dates[1]

    # Convert dates to pandas datetime
    start_date = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date)
    selected_start = start_date.strftime("%d %b %Y")
    selected_end = end_date.strftime("%d %b %Y")
    selected_period = (
        f"**Note:** showing data for the period {selected_start} - {selected_end}."
    )
    st.sidebar.markdown(selected_period)

    return start_date, end_date


# %% Filter by day type


# Setting up sidebar filter for day type (workday or weekend)
def filter_by_day_type():
    possible_day_types = ["Workdays", "Weekends"]
    selected_types = st.sidebar.multiselect(
        "Kinds of days to show", possible_day_types, default=possible_day_types
    )
    # If no option is selected, select all by default
    if not selected_types:
        selected_types = possible_day_types
        st.sidebar.warning(
            "Warning: Data will not be filtered for day type due to empty user selection."
        )

    return selected_types


# %% Filter by hour type


# Setting up sidebar filter for hour type (regular or rush hour)
def filter_by_hour_type():
    possible_h_types = ["Regular hour", "Morning rush hour", "Afternoon rush hour"]
    selected_types = st.sidebar.multiselect(
        "Kinds of hours to show", possible_h_types, default=possible_h_types
    )
    # If no option is selected, select all by default
    if not selected_types:
        selected_types = possible_h_types
        st.sidebar.warning(
            "Warning: Data will not be filtered for hour type due to empty user selection."
        )

    return selected_types


# %% Filter by metro line


# Setting up sidebar filter for metro line
def filter_by_line():
    possible_lines = ["M1", "M2", "M3", "M4"]
    selected_line = st.sidebar.multiselect(
        "Selected lines", possible_lines, default=possible_lines
    )
    # If no option is selected, select all by default
    if not selected_line:
        selected_line = possible_lines
        st.sidebar.warning(
            "Warning: Data will not be filtered for metro line due to empty user selection."
        )

    return selected_line


# %% Filter by downtime period or not


# Setting up sidebar filter for system downtime exclusion
def filter_downtime():
    possible_choices = ["Including system downtime", "Excluding system downtime"]
    selected_choice = st.sidebar.selectbox(
        "Showing data",
        possible_choices,
        index=possible_choices.index("Including system downtime"),
    )
    if selected_choice == "Including system downtime":
        end_choice = [True, False]
    else:
        end_choice = [False]
    return end_choice


# %% Filter by specific station


def filter_by_specific_station() -> str:

    # Getting the unique station names
    query = """
    SELECT DISTINCT station
    FROM station_impact
    ORDER BY station;
    """
    unique_stations = conn.execute(query).fetch_df()
    unique_stations = unique_stations["station"].tolist()

    # Setting up the filter
    selected_station = st.sidebar.selectbox(
        "Station", unique_stations, index=unique_stations.index("Kongens Nytorv")
    )

    return selected_station


# %% Filter by specific travel time/hour interval


def filter_by_travel_time_interval():

    # Getting the unique time intervals
    query = """
    SELECT DISTINCT hour_interval
    FROM station_impact
    ORDER BY hour_interval;
    """
    unique_intervals = conn.execute(query).fetch_df()
    unique_intervals = unique_intervals["hour_interval"].tolist()

    # Setting up the filter
    selected_hour = st.sidebar.selectbox(
        "Time of travel", unique_intervals, index=unique_intervals.index("07-08")
    )

    return selected_hour


# %% Filter by specific weekday


def filter_by_specific_weekday() -> str:

    # Specifying the days in the desired order
    unique_days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    # Setting up the filter
    selected_weekday = st.sidebar.selectbox("Time of travel", unique_days, index=0)

    return selected_weekday


# %%
