"""
============================================
Filters used by the various pages in the app
============================================

Author: github.com/cyrilby
Last meaningful update: 13-10-2026
"""

# %% Setting up

import numpy as np
import pandas as pd
import yaml

from storage import connect_to_db

# Importing long text strings used in the app
with open("text.yaml", "r", encoding="utf-8") as file:
    text = yaml.safe_load(file)

# %% Extracting unique values


def get_unique_days():
    conn = connect_to_db()

    # Extracting values from the data to be used in slicers etc.
    unique_vals = conn.execute(
        "SELECT DISTINCT date, date_in_last_n_days FROM operation_fmt"
    ).df()

    unique_dates = unique_vals["date"].unique().tolist()
    unique_last_n_days = unique_vals["date_in_last_n_days"].unique().tolist()

    n_days = len(unique_dates)
    n_possible_days = np.arange(1, n_days + 1)

    # Preparing a list of (N of) days to use as filter in the app
    unique_dates.sort(reverse=True)
    unique_last_n_days.sort()

    conn.close()

    return unique_dates, unique_last_n_days, n_days, n_possible_days


def get_latest_status():
    conn = connect_to_db()

    # Getting info on the most recent date with data
    query = """
    SELECT
        timestamp,
        line,
        status_en,
        status_dk
    FROM operation_fmt
    WHERE 1=1
        AND timestamp = (
            SELECT MAX(timestamp)
            FROM operation_fmt)
    ORDER BY line;
    """
    most_recent = conn.execute(query).df()

    last_update = most_recent["timestamp"][0]
    last_update_date = last_update.strftime("%d %B %Y")
    last_update_time = last_update.strftime("%H:%M")

    conn.close()

    return most_recent, last_update_date, last_update_time


def get_unique_stations() -> np.ndarray:
    conn = connect_to_db()

    # Extracting the unique names of potentially impacted stations
    query = """
    SELECT DISTINCT station
    FROM station_impact
    ORDER BY station;
    """
    unique_stations = conn.execute(query).fetchnumpy()

    conn.close()

    return unique_stations


def get_unique_intervals() -> np.ndarray:

    conn = connect_to_db()

    # Getting unique intervals and days of time travel
    query = """
    SELECT DISTINCT hour_interval
    FROM station_impact
    ORDER BY hour_interval;
    """
    unique_intervals = conn.execute(query).fetchnumpy()

    conn.close()

    return unique_intervals


def get_unique_day_names() -> list:

    unique_day_names = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    return unique_day_names


def check_missing_mapping() -> pd.DataFrame:

    conn = connect_to_db()

    # Importing user-maintained mapping tables
    mapping_file = "https://github.com/cyrilby/cph-metro-status/raw/refs/heads/main/data/mapping_tables.xlsx"
    mapping_status = pd.read_excel(mapping_file, sheet_name="status")

    # Detecting whether there are any unmapped service status messages
    # as well as the date(s) where data accuracy may be impacted due to lacking mapping
    query = """
    SELECT DISTINCT
        date,
        status_en,
        status_dk
    FROM operation_fmt
    WHERE status_dk NOT IN ?
    """
    mapped_entries = mapping_status["status_dk"].tolist()
    unmapped_msg = conn.execute(query, [mapped_entries]).df()

    query_total_rows = """
    SELECT COUNT(*)
    FROM operation_fmt;
    """
    unmapped_rows = len(unmapped_msg)
    total_rows = conn.execute(query_total_rows).fetchone()[0]
    unmappped_rows_pct = round(100 * ((unmapped_rows + 1) / total_rows), 1)
    unmapped_msg = unmapped_msg.drop_duplicates(subset="status_dk")
    unmapped_msg_n = len(unmapped_msg)

    if unmapped_msg_n:
        unmapped_msg_date_min = unmapped_msg["date"].min()
        unmapped_msg_date_max = unmapped_msg["date"].max()
        if unmapped_msg_date_min == unmapped_msg_date_max:
            unmapped_msg_date_min = None
        else:
            unmapped_msg_date_min = unmapped_msg_date_min.strftime("%d %B %Y")
        unmapped_msg_date_max = unmapped_msg_date_max.strftime("%d %B %Y")

    # Preparing a warning for the app's front page if there are unmapped entries
    if unmapped_msg_n:
        if unmapped_msg_date_min:
            mapping_warning = text["warning_mapping_many_dates"]
            mapping_warning = mapping_warning.format(
                unmapped_msg_n=unmapped_msg_n,
                unmapped_msg_date_min=unmapped_msg_date_min,
                unmapped_msg_date_max=unmapped_msg_date_max,
                unmappped_rows_pct=unmappped_rows_pct,
            )
        else:
            mapping_warning = text["warning_mapping_one_date"]
            mapping_warning = mapping_warning.format(
                unmapped_msg_n=unmapped_msg_n,
                unmapped_msg_date_max=unmapped_msg_date_max,
                unmappped_rows_pct=unmappped_rows_pct,
            )
    else:
        mapping_warning = None

    conn.close()

    return unmapped_msg, mapping_warning
