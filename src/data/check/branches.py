import json
import sys

import pandas as pd

from src.utils.data_loaders import load_df_data


def check_branches(
    prepared_branches: str | pd.DataFrame, prepared_buses: str | pd.DataFrame
) -> dict[str, bool]:
    """Check that branch parameters are correct.

    Args:
        prepared_buses: Path or dataframe to prepared data.
        prepared_branches: Path or dataframe to prepared data.

    Returns:
        Report of checks.
    """
    # To save results
    report = {}

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
    report["There are no NaNs"] = not branches[cols].isna().values.any()

    # Ensure branch names are unique
    report["Branch names are unique"] = branches["branch_name"].is_unique

    # Ensure combinations (from_bus, to_bus, parallel) are unique
    report[
        "There are no duplicated (from_bus, to_bus, parallel)"
    ] = not branches.duplicated(subset=["from_bus", "to_bus", "parallel"]).any()

    # Ensure all values bus names are in the bus dataset
    for col in ["from_bus", "to_bus"]:
        report[f"All bus names in column {col} are present in the bus description"] = (
            branches[col].isin(buses["bus_name"]).all()
        )

    # Correct impedance and current
    report["There are no negative impedances or currents"] = not (
        branches[["r_ohm", "x_ohm", "b_µs", "max_i_ka"]] < 0
    ).values.any()

    # Correct trafo_ratio_rel
    report["There are no non-positive transformation ratios"] = (
        (branches["trafo_ratio_rel"] > 0) | branches["trafo_ratio_rel"].isna()
    ).values.all()
    return report


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 4:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython "
            "check_branches.py path_prepared_branches path_prepared_buses path_report\n"
        )

    # Run
    report = check_branches(prepared_branches=sys.argv[1], prepared_buses=sys.argv[2])

    # Raise if any check fails
    for test_name, result in report.items():
        assert result, f"Failed: {test_name}"

    # Save
    path_report = sys.argv[3]
    with open(path_report, "w") as file:
        json.dump(report, file, indent=4, default=bool)
