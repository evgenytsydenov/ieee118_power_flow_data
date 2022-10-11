import sys

import pandas as pd

from src.utils.data_loaders import load_df_data


def check_ts(
    prepared_loads_ts: str | pd.DataFrame,
    prepared_gens_ts: str | pd.DataFrame,
) -> None:
    """Check that time-series have the same date range.

    Args:
        prepared_loads_ts: Path or dataframe to prepared time-series data.
        prepared_gens_ts: Path or dataframe to prepared time-series data.
    """
    date_range = None
    for name, path in [
        ("load", prepared_loads_ts),
        ("gen", prepared_gens_ts),
    ]:

        # Load data
        data = load_df_data(data=path, dtypes={"datetime": str, f"{name}_name": str})

        # Construct pivot
        data["value"] = True
        pivot = data.pivot_table(index="datetime", columns=f"{name}_name")

        # There are no NaNs in the pivot
        assert (
            not pivot.isna().values.any()
        ), f"Values of {name} time-series dateset has different date ranges."

        # Ensure date ranges are equal
        if date_range is not None:
            pd.testing.assert_index_equal(date_range, pivot.index, check_order=False)
        else:
            date_range = pivot.index


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 3:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython check_ts.py "
            "path_prepared_loads_ts path_prepared_gens_ts\n"
        )

    # Run
    check_ts(
        prepared_loads_ts=sys.argv[1],
        prepared_gens_ts=sys.argv[2],
    )
