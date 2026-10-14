from dataclasses import dataclass

import pandas as pd

from core.filters import (
    filter_by_date_range,
    filter_by_day_type,
    filter_by_hour_type,
    filter_by_line,
    filter_downtime,
)
from core.helpers import deal_with_downtime, deal_with_missing_mapping


@dataclass
class PageData:
    df: pd.DataFrame
    min_date: object
    max_date: object
    downtime_msg: str


def get_filtered_data(conn) -> PageData:

    # Setting up sidebar filters for the data
    min_date, max_date = filter_by_date_range()
    day_types = filter_by_day_type()
    hour_types = filter_by_hour_type()
    selected_lines = filter_by_line()
    selected_rows = filter_downtime()

    # Checking for missing mapping entries
    deal_with_missing_mapping()

    # Querying the database for data
    query = """
        SELECT *
        FROM operation_fmt
        WHERE 1=1
            AND date >= ?
            AND date <= ?
            AND day_type IN ?
            AND official_rush_hour IN ?
            AND line IN ?
        ORDER BY line, date;
    """
    params = [min_date, max_date, day_types, hour_types, selected_lines]
    df = conn.execute(query, params).df()

    # Checking for system downtime
    df, downtime_msg = deal_with_downtime(df, selected_rows)

    return PageData(
        df=df,
        min_date=min_date,
        max_date=max_date,
        downtime_msg=downtime_msg,
    )
