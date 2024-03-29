import sys
from typing import Optional

import numpy as np
import pandas as pd

from definitions import DATE_FORMAT, DATE_RANGE, FILL_METHOD
from src.utils.data_loaders import load_df_data


def prepare_loads_ts(
    transformed_loads: str | pd.DataFrame,
    parsed_nrel118_loads_ts: str | pd.DataFrame,
    path_prepared_data: Optional[str] = None,
) -> Optional[pd.DataFrame]:
    """Prepare final load time-series data.

    Args:
        transformed_loads: Path or dataframe with transformed load data.
        parsed_nrel118_loads_ts: Path or dataframe with time-series load data
          from the NREL-118 dataset.
        path_prepared_data: Path to save prepared data.

    Returns:
        Prepared data or None if `path_prepared_data` is passed and the data were saved.
    """
    # Load data
    interim_loads = load_df_data(
        data=transformed_loads,
        dtypes={
            "load_name": str,
            "region": str,
            "load_participation_factor": float,
            "load_power_factor": float,
        },
    )
    nrel118_loads_ts = load_df_data(
        data=parsed_nrel118_loads_ts,
        dtypes={"region_load": float, "region_name": str, "datetime": str},
    )

    # Calculate active and reactive load at each bus
    loads = nrel118_loads_ts.merge(
        interim_loads, how="right", right_on="region", left_on="region_name"
    )
    loads["p_mw"] = loads["region_load"] * loads["load_participation_factor"]
    loads["q_mvar"] = loads["p_mw"] * np.tan(np.arccos(loads["load_power_factor"]))

    # Assume all loads are in service
    loads["in_service"] = True

    # Extract samples by date
    # Each load has at least one measurement at "2024-01-01 00:00:00"
    start_date, end_date, frequency = DATE_RANGE
    date_range = pd.date_range(
        start_date, end_date, freq=frequency, name="datetime", inclusive="left"
    )

    # Drop Feb 29 since load, wind, and solar data have no this date
    mask = (date_range.day == 29) & (date_range.month == 2)
    date_range = date_range[~mask]

    loads["datetime"] = pd.to_datetime(loads["datetime"], format=DATE_FORMAT)
    loads = (
        loads.sort_values("datetime")
        .set_index("datetime")
        .groupby("load_name")
        .apply(lambda x: x.reindex(date_range, method=FILL_METHOD))
        .drop(columns=["load_name"])
        .round(decimals=6)
        .reset_index()
        .sort_values(["datetime", "load_name"], ignore_index=True)
    )

    # Assumptions
    loads.loc[loads["region_name"] == "r1", ["p_mw", "q_mvar"]] *= 0.65

    # Return results
    cols = ["datetime", "load_name", "in_service", "p_mw", "q_mvar"]
    if path_prepared_data:
        loads[cols].to_csv(
            path_prepared_data, header=True, index=False, date_format=DATE_FORMAT
        )
    else:
        return loads[cols]


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 4:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython "
            "prepare_loads.py path_transformed_loads path_parsed_nrel118_loads_ts "
            "path_prepared_data\n"
        )

    # Run
    prepare_loads_ts(
        transformed_loads=sys.argv[1],
        parsed_nrel118_loads_ts=sys.argv[2],
        path_prepared_data=sys.argv[3],
    )
