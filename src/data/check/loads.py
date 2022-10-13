import json
import sys

import pandas as pd

from src.utils.data_loaders import load_df_data


def check_loads(
    prepared_loads: str | pd.DataFrame, prepared_buses: str | pd.DataFrame
) -> dict[str, bool]:
    """Check that load parameters are correct.

    Args:
        prepared_buses: Path or dataframe to prepared data.
        prepared_loads: Path or dataframe to prepared data.

    Returns:
        Report of checks.
    """
    # To save results
    report = {}

    # Load data
    loads = load_df_data(
        data=prepared_loads, dtypes={"bus_name": str, "load_name": str}
    )
    buses = load_df_data(data=prepared_buses, dtypes={"bus_name": str})

    # Checks
    report["There are no NaNs"] = not loads.isna().values.any()
    report["Load names are unique"] = loads["load_name"].is_unique
    report["All bus names are in the bus description"] = (
        loads["bus_name"].isin(buses["bus_name"]).all()
    )
    report["There is only one load per bus"] = loads["bus_name"].is_unique
    return report


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 4:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython check_loads.py path_prepared_loads "
            "path_prepared_buses path_report\n"
        )

    # Run
    report = check_loads(prepared_loads=sys.argv[1], prepared_buses=sys.argv[2])

    # Raise if any check fails
    for test_name, result in report.items():
        assert result, f"Failed: {test_name}"

    # Save
    path_report = sys.argv[3]
    with open(path_report, "w") as file:
        json.dump(report, file, indent=4, default=bool)
