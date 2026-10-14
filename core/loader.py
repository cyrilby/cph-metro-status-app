from dataclasses import dataclass

import pandas as pd

from core.filters import (
    filter_by_date_range,
    filter_by_day_type,
    filter_by_hour_type,
    filter_by_line,
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
    selected_period: str
    downtime_msg: str


def get_filtered_data(conn, apply_date_filter: bool = True) -> PageData:

    # Setting up sidebar filters for the data
    min_date, max_date = filter_by_date_range()
    day_types = filter_by_day_type()
    hour_types = filter_by_hour_type()
    selected_lines = filter_by_line()
    selected_rows = filter_downtime()

    # Confirming the selected period
    selected_period = get_period_string(min_date, max_date)

    # Checking for missing mapping entries
    deal_with_missing_mapping()

    # Preparing params and optional date filter
    if apply_date_filter:
        date_filter = """
        AND date >= ?
        AND date <= ?
        """
        params = [min_date, max_date, day_types, hour_types, selected_lines]
    else:
        date_filter = ""
        params = [day_types, hour_types, selected_lines]

    # Querying the database for data
    query = f"""
        SELECT *
        FROM operation_fmt
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

    # Checking for system downtime
    df, downtime_msg = deal_with_downtime(df, selected_rows)

    return PageData(
        df=df,
        min_date=min_date,
        max_date=max_date,
        selected_period=selected_period,
        downtime_msg=downtime_msg,
    )
