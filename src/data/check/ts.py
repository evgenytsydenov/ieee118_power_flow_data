import json
import sys

import pandas as pd

from src.utils.data_loaders import load_df_data


def check_ts(
    prepared_loads_ts: str | pd.DataFrame,
    prepared_gens_ts: str | pd.DataFrame,
) -> dict[str, bool]:
    """Check that time-series have the same date range.

    Args:
        prepared_loads_ts: Path or dataframe to prepared time-series data.
        prepared_gens_ts: Path or dataframe to prepared time-series data.

    Returns:
        Report of checks.
    """
    # To save results
    report = {}

    date_range = None
    range_name = None
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
        report[
            f"Parameters of {name} time-series dataset have the same date ranges"
        ] = not pivot.isna().values.any()

        # Ensure date ranges are equal
        if date_range is not None:
            report[
                f"Date ranges in {range_name} and {name} datasets are equal"
            ] = date_range.equals(pivot.index.sort_values())
        else:
            date_range = pivot.index.sort_values()
            range_name = name
    return report


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 4:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython ts.py "
            "path_prepared_loads_ts path_prepared_gens_ts path_report\n"
        )

    # Run
    report = check_ts(
        prepared_loads_ts=sys.argv[1],
        prepared_gens_ts=sys.argv[2],
    )

    # Raise if any check fails
    for test_name, result in report.items():
        assert result, f"Failed: {test_name}"

    # Save
    path_report = sys.argv[3]
    with open(path_report, "w") as file:
        json.dump(report, file, indent=4, default=bool)
