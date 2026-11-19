"""
=======================
Disruption history page
=======================

Author: github.com/cyrilby
Last meaningful update: 19-11-2026
"""

# %% Setting up

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from core.helpers import load_text, plot_or_not
from core.loader import get_filtered_data, set_page_filters
from core.storage import get_app_data

# Importing data and text strings used in the app
text = load_text()
conn = get_app_data()


# %% Common for all data-driven pages

# Page title displayed on top
st.header("Disruption history")

# Source & filter data, deal with warnings, etc.
page_filters = set_page_filters()
data = get_filtered_data(conn, page_filters)

min_date = data.min_date
max_date = data.max_date
n_days = data.n_days
downtime_msg = data.downtime_msg
selected_period = data.selected_period
df = data.df

# Confirming the selected period
st.sidebar.markdown(
    f"**Note:** this selection covers the period between {selected_period}."
    + downtime_msg
)


# %% Functions to load and prepare data for charts


@st.cache_data(show_spinner=False)
def get_daily_disruption(df: pd.DataFrame) -> tuple:
    """
    Prepares datasets with daily disruption metrics
    for the charts shown on this page of the app.
    """

    # Loading additional data used on this page
    query = "SELECT * FROM mapping_stations"
    mapping_stations = conn.execute(query).fetch_df()

    # Note: this range is needed for df merge later on
    date_range = pd.date_range(start=min_date, end=max_date)
    date_range = pd.DataFrame({"date": date_range})

    # Preparing data on disruption durations
    daily_disruption = df.copy()
    daily_disruption["time_diff"] = (
        daily_disruption["disruption_end"] - daily_disruption["disruption_start"]
    ).abs()

    daily_disruption = daily_disruption.loc[
        daily_disruption.groupby(["status_dk", "disruption_end"], observed=True)[
            "time_diff"
        ].idxmin()
    ].copy()

    # Preparing data for daily disruptions
    vars_for_group = ["status_en_short", "date"]

    daily_disruption["rows_for_status"] = daily_disruption.groupby(vars_for_group)[
        "date"
    ].transform("count")

    daily_disruption["unique_msg"] = daily_disruption.groupby(vars_for_group)[
        "status_dk"
    ].transform("nunique")

    daily_disruption["rows_for_date"] = daily_disruption.groupby("date")[
        "date"
    ].transform("count")

    daily_disruption["status_pct"] = 100 * (
        daily_disruption["rows_for_status"] / daily_disruption["rows_for_date"]
    )

    daily_disruption["avg_disr_dur_hours"] = daily_disruption.groupby(vars_for_group)[
        "disruption_duration_hours"
    ].transform("mean")
    daily_disruption["status_pct"] = np.round(daily_disruption["status_pct"], 1)

    daily_disruption["avg_disr_dur_hours"] = np.round(
        daily_disruption["avg_disr_dur_hours"], 1
    )
    daily_disruption = daily_disruption.drop_duplicates(vars_for_group)
    daily_disruption = daily_disruption[
        daily_disruption["status_en_short"] == "Disruption"
    ].copy()

    daily_disruption = daily_disruption.reset_index(drop=True)
    daily_disruption = pd.merge(date_range, daily_disruption, on="date", how="left")
    daily_disruption = daily_disruption.set_index("date")
    daily_disruption = daily_disruption.asfreq("D")
    daily_disruption = daily_disruption.reset_index()

    # Dealing with extreme cases (outliers can
    # occur if the same service message appears
    # at several very different points in time)
    observed_med = daily_disruption["avg_disr_dur_hours"].median()
    tolerance_lvl = 100 * observed_med

    # Note: an outlier is defined as a duration
    # 100 times or more higher than the median
    # duration observed in the given period
    daily_disruption["avg_disr_dur_hours"] = np.where(
        daily_disruption["avg_disr_dur_hours"] <= tolerance_lvl,
        daily_disruption["avg_disr_dur_hours"],
        np.nan,
    )

    # Dealing with potential NANs (we don't always have disruptions)
    daily_disruption["status_pct"] = daily_disruption["status_pct"].fillna(0)

    daily_disruption["unique_msg"] = daily_disruption["unique_msg"].fillna(0)

    # Note: for this specific indicator, we
    # impute with the average so as not to skew
    # our subsequent data aggregation
    daily_disruption["avg_disr_dur_hours"] = daily_disruption[
        "avg_disr_dur_hours"
    ].fillna(daily_disruption["avg_disr_dur_hours"].mean())

    # Preparing data for the N of stations impacted by day
    n_total_stations = len(mapping_stations["station"].unique())
    daily_disr_stations = df.copy()
    daily_disr_stations["avg_n_impacted"] = daily_disr_stations.groupby("date")[
        "n_impacted_stations"
    ].transform("mean")
    daily_disr_stations["avg_pct_impacted"] = 100 * (
        daily_disr_stations["avg_n_impacted"] / n_total_stations
    )
    daily_disr_stations["avg_pct_impacted"] = np.round(
        daily_disr_stations["avg_pct_impacted"], 1
    )
    daily_disr_stations = daily_disr_stations.drop_duplicates("date")
    daily_disr_stations = daily_disr_stations.reset_index(drop=True)

    return daily_disruption, daily_disr_stations


# %% Specific page content

# Loading and preparing data
daily_disruption, daily_disr_stations = get_daily_disruption(df)

# Preparing KPI metrics for the page
total_disruptions = int(daily_disruption["unique_msg"].sum())
n_days = len(daily_disruption["date"].unique())
avg_per_day = total_disruptions / n_days
avg_duration = daily_disruption["avg_disr_dur_hours"].mean()

# Rounding off numbers to be used as KPIs
total_disruptions = round(total_disruptions, 0)
avg_per_day = round(avg_per_day, 1)
avg_duration = round(avg_duration, 1)

# Creating a bar chart that shows N of service disruptions per day
n_disr_chart = px.bar(
    daily_disruption,
    x="date",
    y="unique_msg",
)
n_disr_chart.update_layout(
    title_text=f"Disruptions per day during the last {n_days} days"
)
n_disr_chart.update_xaxes(title_text="Date")
n_disr_chart.update_yaxes(title_text="Disruptions per day")

# Creating a line chart that shows service disruptions as % of time
pct_disr_chart = px.line(
    daily_disruption,
    x="date",
    y="status_pct",
)
pct_disr_chart.update_layout(
    title_text=f"Disruptions in the metro's service in the last {n_days} days, % of time"
)
pct_disr_chart.update_xaxes(title_text="Date")
pct_disr_chart.update_yaxes(title_text="Disruptions, % of time")

# Creating a line chart that shows the average duration of the disruptions
h_disr_chart = px.line(
    daily_disruption,
    x="date",
    y="avg_disr_dur_hours",
)
h_disr_chart.update_layout(
    title_text=f"Average duration of disruptions in the last {n_days} days (measured in hours)"
)
h_disr_chart.update_xaxes(title_text="Date")
h_disr_chart.update_yaxes(title_text="Average duration (hours)")

# Creating a line chart that shows average % of stations impacted by day
stations_chart_pct = px.line(
    daily_disr_stations,
    x="date",
    y="avg_pct_impacted",
)
stations_chart_pct.update_layout(
    title_text=f"Average % of impacted stations in the last {n_days} days"
)
stations_chart_pct.update_xaxes(title_text="Date")
stations_chart_pct.update_yaxes(title_text="Average % of stations impacted")

# Creating a bar chart that shows average N of stations impacted by day
stations_chart = px.bar(
    daily_disr_stations,
    x="date",
    y="avg_n_impacted",
)
stations_chart.update_layout(
    title_text=f"Average number of impacted stations in the last {n_days} days"
)
stations_chart.update_xaxes(title_text="Date")
stations_chart.update_yaxes(title_text="Average number of stations impacted")

# Preparing messages describing the charts
n_desc = text["hist_n_desc"]
pct_desc = text["hist_pct_desc"]
h_desc = text["hist_h_desc"]
stations_desc_pct = text["hist_stations_desc_pct"]
stations_desc = text["hist_stations_desc"]

# Plotting the elements in the correct order,
# starting with KPIs on top of the page and proceeding with charts
msg_text = text["hist_page_desc"]
msg_text = msg_text.format(selected_period=selected_period)
st.markdown(msg_text)

metric1, metric2, metric3 = st.columns(3)
metric1.metric("Total disruptions", str(total_disruptions))
metric2.metric("Average disruptions per day", str(avg_per_day))
metric3.metric("Average duration", str(avg_duration) + "h")

st.subheader("Number of disruptions", divider="grey")
st.markdown(n_desc)
plot_or_not(n_disr_chart, daily_disruption)

st.subheader("Disruptions as % of time", divider="grey")
st.markdown(pct_desc)
plot_or_not(pct_disr_chart, daily_disruption)

st.subheader("Duration of disruptions", divider="grey")
st.markdown(h_desc)
plot_or_not(h_disr_chart, daily_disruption)

st.subheader("Impacted stations", divider="grey")
st.markdown(stations_desc_pct)
plot_or_not(stations_chart_pct, daily_disr_stations)

st.markdown(stations_desc)
plot_or_not(stations_chart, daily_disr_stations)


# %%
