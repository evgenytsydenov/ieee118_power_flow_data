import sys

import numpy as np
import pandas as pd

from src.utils.data_loaders import load_df_data


def check_gens_ts(
    prepared_gens_ts: str | pd.DataFrame,
    prepared_gens: str | pd.DataFrame,
) -> None:
    """Check that generator time-series values are correct.

    Args:
        prepared_gens_ts: Path or dataframe to prepared time-series data.
        prepared_gens: Path or dataframe to prepared data.
    """
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
    assert (
        not gens_ts[["datetime", "gen_name", "in_service"]].isna().values.any()
    ), "There are missing obligatory parameters"

    # Ensure parameters are undefined when gen is out of service
    value_cols = ["v_set_kv", "p_mw", "q_min_mvar", "q_max_mvar"]
    assert (
        gens_ts.loc[~gens_ts["in_service"], value_cols].isna().values.all()
    ), "There are value of parameters when generator is out of service"

    # Ensure there are no NaNs when gens are in service
    gens_in_service = gens_ts[gens_ts["in_service"]]
    assert (
        not gens_in_service.isna().values.any()
    ), "There are undefined parameters when generator is in service"

    # Some values should not be negative
    assert (gens_in_service["p_mw"] >= 0).values.all(), "Some gens have negative output"
    assert (
        gens_in_service["v_set_kv"] >= 0
    ).values.all(), "Some gens have negative voltage"

    # Check reactive output
    assert (
        gens_in_service["q_min_mvar"] <= gens_in_service["q_max_mvar"]
    ).values.all(), (
        "Min level of reactive output of some gens are greater than Max level"
    )

    # Ensure there are time-series values for all gens
    gens_ts_names = gens_ts["gen_name"].unique()
    gens_names = gens["gen_name"].unique()
    assert np.isin(
        gens_names, gens_ts_names, assume_unique=True
    ).all(), "Some gens are missed in time-series data"
    assert np.isin(
        gens_ts_names, gens_names, assume_unique=True
    ).all(), "There are some unknown gens in time-series data"


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 3:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython check_gens_ts.py "
            "path_prepared_gens_ts path_prepared_gens\n"
        )

    # Run
    check_gens_ts(prepared_gens_ts=sys.argv[1], prepared_gens=sys.argv[2])
