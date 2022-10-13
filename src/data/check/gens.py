import json
import sys

import pandas as pd

from definitions import PLANT_MODE
from src.utils.data_loaders import load_df_data


def check_gens(
    prepared_gens: str | pd.DataFrame, prepared_buses: str | pd.DataFrame
) -> dict[str, bool]:
    """Check that generator parameters are correct.

    Args:
        prepared_buses: Path or dataframe to prepared data.
        prepared_gens: Path or dataframe to prepared data.

    Returns:
        Report of checks.
    """
    # To save results
    report = {}

    # Load data
    gens = load_df_data(data=prepared_gens, dtypes={"bus_name": str, "gen_name": str})
    buses = load_df_data(data=prepared_buses, dtypes={"bus_name": str})

    # Checks
    report["There are no NaNs"] = not gens.isna().values.any()
    report["Gen names are unique"] = gens["gen_name"].is_unique
    report["All bus names are in the bus description"] = (
        gens["bus_name"].isin(buses["bus_name"]).all()
    )

    # Ensure there is only one plant per bus
    if PLANT_MODE:
        report["There is only one plant per bus"] = gens["bus_name"].is_unique
    return report


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 4:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython check_gens.py path_prepared_gens "
            "path_prepared_buses path_report\n"
        )

    # Run
    report = check_gens(prepared_gens=sys.argv[1], prepared_buses=sys.argv[2])

    # Raise if any check fails
    for test_name, result in report.items():
        assert result, f"Failed: {test_name}"

    # Save
    path_report = sys.argv[3]
    with open(path_report, "w") as file:
        json.dump(report, file, indent=4, default=bool)
