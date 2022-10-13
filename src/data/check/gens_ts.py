import json
import sys

import numpy as np
import pandas as pd

from src.utils.data_loaders import load_df_data


def check_gens_ts(
    prepared_gens_ts: str | pd.DataFrame,
    prepared_gens: str | pd.DataFrame,
) -> dict[str, bool]:
    """Check that generator time-series values are correct.

    Args:
        prepared_gens_ts: Path or dataframe to prepared time-series data.
        prepared_gens: Path or dataframe to prepared data.

    Returns:
        Report of checks.
    """
    # To save results
    report = {}

    # Load data
    gens = load_df_data(data=prepared_gens, dtypes={"gen_name": str})
    gens_ts = load_df_data(
        data=prepared_gens_ts,
        dtypes={
            "datetime": str,
            "gen_name": str,
            "in_service": bool,
            "q_max_mvar": float,
            "q_min_mvar": float,
            "p_mw": float,
            "v_set_kv": float,
        },
    )

    # Ensure there are no NaNs among obligatory values
    report["There are no NaNs among obligatory values"] = (
        not gens_ts[["datetime", "gen_name", "in_service"]].isna().values.any()
    )

    # Ensure parameters are undefined when gen is out of service
    value_cols = ["v_set_kv", "p_mw", "q_min_mvar", "q_max_mvar"]
    report["Parameters are undefined when gen is out of service"] = (
        gens_ts.loc[~gens_ts["in_service"], value_cols].isna().values.all()
    )

    # Ensure there are no NaNs when gens are in service
    gens_in_service = gens_ts[gens_ts["in_service"]]
    report[
        "There are no NaNs when gens are in service"
    ] = not gens_in_service.isna().values.any()

    # Some values should not be negative
    report["Active output is always positive"] = (gens_in_service["p_mw"] >= 0).all()
    report["Voltage set is always positive"] = (gens_in_service["v_set_kv"] >= 0).all()

    # Check reactive output
    report["Max level of reactive output is always greater than Min level"] = (
        gens_in_service["q_min_mvar"] <= gens_in_service["q_max_mvar"]
    ).all()

    # Ensure there are time-series values for all gens
    gens_ts_names = gens_ts["gen_name"].unique()
    gens_names = gens["gen_name"].unique()
    report["All gens are present in time-series data"] = np.isin(
        gens_names, gens_ts_names, assume_unique=True
    ).all()
    report[
        "All gens from time-series data are present in the gen description"
    ] = np.isin(gens_ts_names, gens_names, assume_unique=True).all()
    return report


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 4:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython check_gens_ts.py "
            "path_prepared_gens_ts path_prepared_gens path_report\n"
        )

    # Run
    report = check_gens_ts(prepared_gens_ts=sys.argv[1], prepared_gens=sys.argv[2])

    # Raise if any check fails
    for test_name, result in report.items():
        assert result, f"Failed: {test_name}"

    # Save
    path_report = sys.argv[3]
    with open(path_report, "w") as file:
        json.dump(report, file, indent=4, default=bool)
