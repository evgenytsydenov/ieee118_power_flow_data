import json
import sys

import pandas as pd

from src.utils.data_loaders import load_df_data


def check_buses(prepared_buses: str | pd.DataFrame) -> dict[str, bool]:
    """Check that bus parameters are correct.

    Args:
        prepared_buses: Path or dataframe to prepared data.

    Returns:
        Report of checks.
    """
    # Load data
    buses = load_df_data(
        data=prepared_buses,
        dtypes={
            "bus_name": str,
            "region": str,
            "in_service": bool,
            "v_rated_kv": float,
        },
    )

    # Save results
    report = {
        "There are no NaNs": not buses.isna().values.any(),
        "Bus names are unique": buses["bus_name"].is_unique,
    }
    return report


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 3:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython "
            "check_buses.py path_prepared_buses path_report\n"
        )

    # Run
    report = check_buses(prepared_buses=sys.argv[1])

    # Raise if any check fails
    for test_name, result in report.items():
        assert result, f"Failed: {test_name}"

    # Save
    path_report = sys.argv[2]
    with open(path_report, "w") as file:
        json.dump(report, file, indent=4, default=bool)
