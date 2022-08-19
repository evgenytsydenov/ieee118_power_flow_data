import sys

import pandas as pd

from src.utils.data_loaders import load_df_data


def check_loads_ts(
    prepared_loads_ts: str | pd.DataFrame,
    prepared_loads: str | pd.DataFrame,
) -> None:
    """Check that load parameters are correct.

    Args:
        prepared_loads_ts: Path or dataframe to prepared time-series data.
        prepared_loads: Path or dataframe to prepared data.
    """
    # Load data
    loads = load_df_data(
        data=prepared_loads,
        dtypes={
            "bus_name": str,
            "load_name": str,
        },
    )
    loads_ts = pd.read_csv(
        prepared_loads_ts,
        header=[0, 1],
        index_col=0,
        dtype={"in_service": bool, "q_mvar": float, "p_mw": float},
    )

    # Ensure there are no NaNs
    assert not loads_ts.isna().values.any(), "There are NaNs in the dataset"

    # Ensure there are time-series values for all loads
    for parameter in loads_ts.columns.levels[0]:
        load_names = loads_ts[parameter].columns
        assert load_names.isin(
            loads["load_name"]
        ).all(), "There are some unknown loads in time-series data"
        assert (
            loads["load_name"].isin(load_names).all()
        ), "Some loads are missed in time-series data"

    # Demand should not be negative
    for parameter in ["p_mw", "q_mvar"]:
        assert (
            loads_ts[parameter] >= 0
        ).values.all(), "Some loads have negative demand"


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 3:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython check_loads_ts.py "
            "path_prepared_loads_ts path_prepared_loads\n"
        )

    # Run
    check_loads_ts(prepared_loads_ts=sys.argv[1], prepared_loads=sys.argv[2])
