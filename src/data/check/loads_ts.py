import json
import sys

import numpy as np
import pandas as pd

from src.utils.data_loaders import load_df_data


def check_loads_ts(
    prepared_loads_ts: str | pd.DataFrame,
    prepared_loads: str | pd.DataFrame,
) -> dict[str, bool]:
    """Check that load time-series values are correct.

    Args:
        prepared_loads_ts: Path or dataframe to prepared time-series data.
        prepared_loads: Path or dataframe to prepared data.

    Returns:
        Report of checks.
    """
    # To save results
    report = {}

    # Load data
    loads = load_df_data(
        data=prepared_loads,
        dtypes={
            "bus_name": str,
            "load_name": str,
        },
    )
    loads_ts = load_df_data(
        data=prepared_loads_ts,
        dtypes={
            "datetime": str,
            "load_name": str,
            "in_service": bool,
            "q_mvar": float,
            "p_mw": float,
        },
    )

    # Ensure there are no NaNs
    report["There are no NaNs"] = not loads_ts.isna().values.any()

    # Ensure there are time-series values for all loads
    loads_ts_names = loads_ts["load_name"].unique()
    loads_names = loads["load_name"].unique()
    report["All loads are present in time-series data"] = np.isin(
        loads_names, loads_ts_names, assume_unique=True
    ).all()
    report[
        "All loads from time-series data are present in the load description"
    ] = np.isin(loads_ts_names, loads_names, assume_unique=True).all()

    # Demand should not be negative
    for parameter in ["p_mw", "q_mvar"]:
        report[f"There are no negative values in column {parameter}"] = (
            loads_ts[parameter] >= 0
        ).all()
    return report


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 4:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython loads_ts.py "
            "path_prepared_loads_ts path_prepared_loads path_report\n"
        )

    # Run
    report = check_loads_ts(prepared_loads_ts=sys.argv[1], prepared_loads=sys.argv[2])

    # Raise if any check fails
    for test_name, result in report.items():
        assert result, f"Failed: {test_name}"

    # Save
    path_report = sys.argv[3]
    with open(path_report, "w") as file:
        json.dump(report, file, indent=4, default=bool)
