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

    Raises:
        AssertionError: Some check fails.
    """
    # Load data
    gens = load_df_data(
        data=prepared_gens,
        dtypes={
            "gen_name": str,
            "opt_category": str,
        },
    )
    gens_ts = load_df_data(
        data=prepared_gens_ts,
        dtypes={
            "datetime": str,
            "gen_name": str,
            "in_service": bool,
            "p_mw": float,
            "max_q_mvar": float,
            "min_q_mvar": float,
            "max_p_mw": float,
            "min_p_mw": float,
        },
    )

    # Ensure there are no NaNs among obligatory values
    assert (
        not gens_ts[["datetime", "gen_name", "in_service"]].isna().values.any()
    ), "There are missing obligatory parameters"

    # Ensure there are time-series values for all gens
    gens_ts_names = gens_ts["gen_name"].unique()
    gens_names = gens["gen_name"].unique()
    assert np.isin(
        gens_names, gens_ts_names, assume_unique=True
    ).all(), "Some gens are missed in the time-series data"
    assert np.isin(
        gens_ts_names, gens_names, assume_unique=True
    ).all(), "There are some unknown gens in the time-series data"

    # Precompute
    values = ["p_mw"]
    limits = ["min_q_mvar", "max_q_mvar", "max_p_mw", "min_p_mw"]
    optimized_names = gens.loc[gens["opt_category"] != "non_optimized", "gen_name"]
    gens_optimized = gens_ts["gen_name"].isin(optimized_names)
    gens_in_service = gens_ts["in_service"]

    # Ensure parameters are undefined when gen is out of service
    assert (
        gens_ts.loc[~gens_in_service, values + limits].isna().values.all()
    ), "There are parameters when generator is out of service"

    # Ensure there are no NaNs among gen limits when gens are in service
    assert (
        not gens_ts.loc[gens_in_service, limits].isna().values.any()
    ), "There are undefined gen limits when generator is in service"

    # Ensure parameters are no NaNs when gens are in service and not optimized
    assert (
        not gens_ts.loc[gens_in_service & ~gens_optimized, values].isna().values.any()
    ), "There are undefined parameters when generator is not optimized and in service"

    # Ensure parameters are undefined when gen is in service and optimized
    assert (
        gens_ts.loc[gens_in_service & gens_optimized, values].isna().values.all()
    ), "There are defined parameters when generator is optimized and in service"

    # Some values should not be negative
    assert (
        gens_ts.loc[gens_in_service & ~gens_optimized, "p_mw"] >= 0
    ).all(), "Some gens have negative output"

    # Check reactive output limits
    assert (
        gens_ts.loc[gens_in_service, "min_q_mvar"]
        <= gens_ts.loc[gens_in_service, "max_q_mvar"]
    ).all(), "Min level of reactive output of some gens are greater than the max level"

    # Check active output limits
    assert (
        gens_ts.loc[gens_in_service, "min_p_mw"]
        <= gens_ts.loc[gens_in_service, "max_p_mw"]
    ).all(), "Min level of active output of some gens are greater than the max level"

    # Ensure each gen has values for each timestamp
    pivot = gens_ts[["datetime", "gen_name", "in_service"]].pivot_table(
        index="datetime", columns="gen_name"
    )
    assert (
        not pivot.isna().values.any()
    ), "Values of the gen time-series dataset has different date ranges."


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 3:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython check_gens_ts.py "
            "path_prepared_gens_ts path_prepared_gens\n"
        )

    # Run
    check_gens_ts(prepared_gens_ts=sys.argv[1], prepared_gens=sys.argv[2])
