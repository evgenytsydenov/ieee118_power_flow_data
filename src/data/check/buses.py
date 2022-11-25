import sys

import pandas as pd

from src.utils.data_loaders import load_df_data


def check_buses(prepared_buses: str | pd.DataFrame) -> None:
    """Check that bus parameters are correct.

    Args:
        prepared_buses: Path or dataframe to prepared data.

    Raises:
        AssertionError: Some check fails.
    """
    # Load data
    buses = load_df_data(
        data=prepared_buses,
        dtypes={
            "bus_name": str,
            "region": str,
            "in_service": bool,
            "v_rated_kv": float,
            "is_slack": bool,
            "min_v_pu": float,
            "max_v_pu": float,
            "x_coordinate": float,
            "y_coordinate": float,
        },
    )

    # Ensure there are no NaNs
    assert not buses.isna().values.any(), "There are NaNs in the dataset"

    # Ensure bus names are unique
    assert buses["bus_name"].is_unique, "There are duplicated bus names"

    # There is only one slack bus
    assert buses["is_slack"].sum() == 1, "Number of slack buses is not equal to one"

    # Min limit should be less than the max one
    assert (
        buses["min_v_pu"] <= buses["max_v_pu"]
    ).all(), "Min limit of some buses is greater than the max one."


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 2:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython "
            "check_buses.py path_prepared_buses\n"
        )

    # Run
    check_buses(prepared_buses=sys.argv[1])
