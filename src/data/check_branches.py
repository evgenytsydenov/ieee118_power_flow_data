import sys

import pandas as pd

from src.utils.data_loaders import load_df_data


def check_branches(prepared_branches: str | pd.DataFrame) -> None:
    """Check that branch parameters are correct.

    Args:
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
            "trafo_ratio": float,
            "max_i_ka": float,
        },
    )

    # Ensure there are no NaNs
    cols = [col for col in branches.columns if col != "trafo_ratio"]
    assert not branches[cols].isna().values.any(), "There are NaNs in the dataset"

    # Ensure bus names are unique
    assert branches["branch_name"].is_unique, "There are duplicated branch names"

    # Ensure combinations (from_bus, to_bus, parallel) are unique
    assert not branches.duplicated(
        subset=["from_bus", "to_bus", "parallel"]
    ).any(), "There are duplicated (from_bus, to_bus, parallel)"

    # Correct impedance and current
    assert not (
        branches[["r_ohm", "x_ohm", "b_µs", "max_i_ka"]] < 0
    ).values.any(), "There are negative impedance or current"

    # Correct trafo_ratio
    assert (
        (branches["trafo_ratio"] > 0) | branches["trafo_ratio"].isna()
    ).all(), "There are non-positive transformation ratios"


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 2:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython "
            "check_branches.py path_prepared_branches\n"
        )

    # Run
    check_branches(prepared_branches=sys.argv[1])
