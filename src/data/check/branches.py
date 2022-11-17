import sys

import pandas as pd

from src.utils.data_loaders import load_df_data


def check_branches(
    prepared_branches: str | pd.DataFrame, prepared_buses: str | pd.DataFrame
) -> None:
    """Check that branch parameters are correct.

    Args:
        prepared_buses: Path or dataframe to prepared data.
        prepared_branches: Path or dataframe to prepared data.
    """
    # Load data
    branches = load_df_data(
        data=prepared_branches,
        dtypes={
            "branch_name": str,
            "from_bus": str,
            "to_bus": str,
            "parallel": str,
            "in_service": bool,
            "r_ohm": float,
            "x_ohm": float,
            "b_µs": float,
            "trafo_ratio_rel": float,
            "max_i_ka": float,
        },
    )
    buses = load_df_data(data=prepared_buses, dtypes={"bus_name": str})

    # Ensure there are no NaNs
    cols = [col for col in branches.columns if col != "trafo_ratio_rel"]
    assert not branches[cols].isna().values.any(), "There are NaNs in the dataset"

    # Ensure branch names are unique
    assert branches["branch_name"].is_unique, "There are duplicated branch names"

    # Ensure combinations (from_bus, to_bus, parallel) are unique
    assert not branches.duplicated(
        subset=["from_bus", "to_bus", "parallel"]
    ).any(), "There are duplicated (from_bus, to_bus, parallel)"

    # Ensure all values (from_bus, to_bus) are in the bus dataset
    for col in ["from_bus", "to_bus"]:
        assert (
            branches[col].isin(buses["bus_name"]).all()
        ), f"There are unknown bus names in the column {col}"

    # Correct impedance and current
    assert (
        branches[["r_ohm", "x_ohm", "b_µs", "max_i_ka"]] >= 0
    ).values.all(), "There are negative impedance values or current limits"

    # Correct trafo_ratio_rel
    assert (
        (branches["trafo_ratio_rel"] > 0) | branches["trafo_ratio_rel"].isna()
    ).all(), "There are non-positive transformation ratios"


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 3:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython "
            "check_branches.py path_prepared_branches path_prepared_buses\n"
        )

    # Run
    check_branches(prepared_branches=sys.argv[1], prepared_buses=sys.argv[2])
