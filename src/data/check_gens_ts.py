import sys

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
    gens_ts = pd.read_csv(
        prepared_gens_ts,
        header=[0, 1],
        index_col=0,
        dtype={
            "in_service": bool,
            "q_max_mvar": float,
            "q_min_mvar": float,
            "p_mw": float,
            "v_set_kv": float,
        },
    )

    # Output should not be negative
    assert (gens_ts["p_mw"] >= 0).values.all(), "Some gens have negative output"

    # Ensure there are no NaNs
    # assert not gens.isna().values.any(), "There are NaNs in the dataset"

    # Ensure there are time-series values for all gens
    for parameter in gens_ts.columns.levels[0]:
        gen_names = gens_ts[parameter].columns
        assert gen_names.isin(
            gens["gen_name"]
        ).all(), "There are some unknown gens in time-series data"
        assert (
            gens["gen_name"].isin(gen_names).all()
        ), "Some gens are missed in time-series data"


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 3:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython check_gens_ts.py "
            "path_prepared_gens_ts path_prepared_gens\n"
        )

    # Run
    check_gens_ts(prepared_gens_ts=sys.argv[1], prepared_gens=sys.argv[2])
