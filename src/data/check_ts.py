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
    loads_ts = pd.read_csv(prepared_loads_ts, usecols=["datetime", "load_name"])
    gens_ts = pd.read_csv(prepared_gens_ts, usecols=["datetime", "gen_name"])

    # Construct pivots
    gen_pivot = gens_ts.pivot_table(index="datetime", columns="gen_name")
    load_pivot = loads_ts.pivot_table(index="datetime", columns="load_name")

    # Ensure date ranges are equal
    pd.testing.assert_index_equal(gen_pivot.index, load_pivot.index, check_order=False)


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 3:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython check_ts.py "
            "path_prepared_loads_ts path_prepared_gens_ts\n"
        )

    # Run
    check_ts(prepared_loads_ts=sys.argv[1], prepared_gens_ts=sys.argv[2])
