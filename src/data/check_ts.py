import sys

import pandas as pd


def check_ts(
    prepared_loads_ts: str | pd.DataFrame,
    prepared_gens_ts: str | pd.DataFrame,
) -> None:
    """Check that time-series have the same date range.

    Args:
        prepared_loads_ts: Path or dataframe to prepared time-series data.
        prepared_gens_ts: Path or dataframe to prepared time-series data.
    """
    # Load data
    loads_ts = pd.read_csv(prepared_loads_ts, skiprows=2, usecols=["datetime"])
    gens_ts = pd.read_csv(prepared_gens_ts, skiprows=2, usecols=["datetime"])

    # Ensure date ranges are equal
    pd.testing.assert_series_equal(loads_ts["datetime"], gens_ts["datetime"])


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 3:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython check_ts.py "
            "path_prepared_loads_ts path_prepared_gens_ts\n"
        )

    # Run
    check_ts(prepared_loads_ts=sys.argv[1], prepared_gens_ts=sys.argv[2])
