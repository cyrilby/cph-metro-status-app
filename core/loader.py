from dataclasses import dataclass

import pandas as pd

from core.filters import (
    filter_by_date_range,
    filter_by_day_type,
    filter_by_hour_type,
    filter_by_line,
    filter_by_specific_station,
    filter_by_specific_weekday,
    filter_by_travel_time_interval,
    filter_downtime,
)
from core.helpers import (
    deal_with_downtime,
    deal_with_missing_mapping,
    get_period_string,
)


@dataclass
class PageData:
    df: pd.DataFrame
    min_date: object
    max_date: object
    n_days: int
    selected_period: str
    downtime_msg: str


@dataclass
class PageFilters:
    min_date: object
    max_date: object
    day_types: list
    hour_types: list
    selected_lines: list
    selected_rows: list


@dataclass
class PageFiltersCalc:
    min_date: object
    max_date: object
    station: object
    travel_time: object
    travel_day: object


@dataclass
class PageDataCalc:
    df: pd.DataFrame
    min_date: object
    max_date: object
    n_days: int
    selected_period: str
    selected_station: object
    selected_travel_time: object
    selected_travel_day: object


def set_page_filters():

    # Setting up sidebar filters for the data
    min_date, max_date = filter_by_date_range()
    day_types = filter_by_day_type()
    hour_types = filter_by_hour_type()
    selected_lines = filter_by_line()
    selected_rows = filter_downtime()

    # Checking for missing mapping entries
    deal_with_missing_mapping()

    return PageFilters(
        min_date=min_date,
        max_date=max_date,
        day_types=day_types,
        hour_types=hour_types,
        selected_lines=selected_lines,
        selected_rows=selected_rows,
    )


def set_page_filters_calc():

    # Setting up sidebar filters for the data
    min_date, max_date = filter_by_date_range()
    station = filter_by_specific_station()
    travel_time = filter_by_travel_time_interval()
    travel_day = filter_by_specific_weekday()

    return PageFiltersCalc(
        min_date=min_date,
        max_date=max_date,
        station=station,
        travel_time=travel_time,
        travel_day=travel_day,
    )


def get_filtered_data(
    conn,
    page_filters,
    table_name: str = "operation_fmt",
    apply_date_filter: bool = True,
) -> PageData:
    """
    This function is used across all app pages except for
    the "Disruption calculator" page.
    """

    # Extracting info from page filters
    min_date = page_filters.min_date
    max_date = page_filters.max_date
    day_types = page_filters.day_types
    hour_types = page_filters.hour_types
    selected_lines = page_filters.selected_lines
    selected_rows = page_filters.selected_rows

    # Confirming the selected period
    selected_period = get_period_string(min_date, max_date)

    # Preparing params and optional date filter
    if apply_date_filter:
        date_filter = """
        AND date >= ?
        AND date <= ?
        """
        params = [
            min_date.strftime("%Y-%m-%d"),
            max_date.strftime("%Y-%m-%d"),
            day_types,
            hour_types,
            selected_lines,
        ]
    else:
        date_filter = ""
        params = [day_types, hour_types, selected_lines]

    # WIP: Deal with missing rush hour (and maybe other)  columns
    # in the station_impact table in the DB: consider having
    # thesefilters at the bottom of the query and params.appenx(x) if table_name = "operation_fmt"

    # Querying the database for data
    query = f"""
        SELECT *
        FROM {table_name}
        WHERE 1=1
            {date_filter}
            AND day_type IN ?
            AND official_rush_hour IN ?
            AND line IN ?
        ORDER BY line, date;
    """
    df = conn.execute(query, params).df()

    # Correcting certain dtypes from the database
    # Note: these are needed because of inconsistencies between
    # different versions of pandas and some other pkgs
    df["date"] = pd.to_datetime(df["date"]).astype("datetime64[ns]")

    # Confirming the number of days fetched
    n_days = df["date"].nunique()

    # Checking for system downtime
    df, downtime_msg = deal_with_downtime(df, selected_rows)

    return PageData(
        df=df,
        min_date=min_date,
        max_date=max_date,
        n_days=n_days,
        selected_period=selected_period,
        downtime_msg=downtime_msg,
    )


def get_filtered_data_calc(
    conn,
    page_filters,
) -> PageData:
    """
    This function is exclusively used on the "Disruption
    calculator" page.
    """

    # Extracting info from page filters
    min_date = page_filters.min_date
    max_date = page_filters.max_date
    station = page_filters.station
    travel_time = page_filters.travel_time
    travel_day = page_filters.travel_day

    # Confirming the selected period
    selected_period = get_period_string(min_date, max_date)

    # Preparing params and obligatory date filter
    date_filter = """
    AND date >= ?
    AND date <= ?
    """
    params = [
        min_date.strftime("%Y-%m-%d"),
        max_date.strftime("%Y-%m-%d"),
        station,
        travel_time,
        travel_day,
    ]

    # WIP: Deal with missing rush hour (and maybe other)  columns
    # in the station_impact table in the DB: consider having
    # thesefilters at the bottom of the query and params.appenx(x) if table_name = "operation_fmt"

    # Querying the database for data
    query = f"""
        SELECT *
        FROM station_impact
        WHERE 1=1
            {date_filter}
            AND station = ?
            AND hour_interval = ?
            AND weekday = ?
        ORDER BY line, date;
    """
    df = conn.execute(query, params).df()

    # Correcting certain dtypes from the database
    # Note: these are needed because of inconsistencies between
    # different versions of pandas and some other pkgs
    df["date"] = pd.to_datetime(df["date"]).astype("datetime64[ns]")

    # Confirming the number of days fetched
    n_days = df["date"].nunique()

    return PageDataCalc(
        df=df,
        min_date=min_date,
        max_date=max_date,
        n_days=n_days,
        selected_period=selected_period,
        selected_station=station,
        selected_travel_time=travel_time,
        selected_travel_day=travel_day,
    )
