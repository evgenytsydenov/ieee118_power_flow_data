import sys

import numpy as np
import pandas as pd

from src.utils.data_loaders import load_df_data


def check_gens_ts(
    prepared_gens_ts: str | pd.DataFrame,
    prepared_gens: str | pd.DataFrame,
) -> None:
    """Check that load parameters are correct.

    Args:
        prepared_gens_ts: Path or dataframe to prepared time-series data.
        prepared_gens: Path or dataframe to prepared data.
    """
    # Load data
    gens = load_df_data(
        data=prepared_gens,
        dtypes={
            "bus_name": str,
            "gen_name": str,
        },
    )
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

    # Some values should not be negative
    assert (gens_ts["p_mw"] >= 0).values.all(), "Some gens have negative output"
    assert (gens_ts["v_set_kv"] >= 0).values.all(), "Some gens have negative voltage"

    # Check reactive output
    assert (
        gens_ts["q_min_mvar"] <= gens_ts["q_max_mvar"]
    ).values.all(), (
        "Min level of reactive output of some gens are greater than Max level"
    )

    # Ensure there are no NaNs
    assert not gens.isna().values.any(), "There are NaNs in the dataset"

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
