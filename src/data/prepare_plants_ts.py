import sys
from typing import Optional

import numpy as np
import pandas as pd

from src.utils.data_loaders import load_df_data


def prepare_plants_ts(
    prepared_plants: str | pd.DataFrame,
    prepared_gens_ts: str | pd.DataFrame,
    path_prepared_data: Optional[str] = None,
) -> Optional[pd.DataFrame]:
    """Prepare final plant time-series data.

    Args:
        prepared_plants: Path or dataframe with prepared plant data.
        prepared_gens_ts: Path or dataframe with time-series generation data.
        path_prepared_data: Path to save prepared data.

    Returns:
        Prepared data or None if `path_prepared_data` is passed and the data were saved.
    """
    # Load data
    plants = load_df_data(
        data=prepared_plants,
        dtypes={"gen_name": str, "plant_name": str},
    )
    gens_ts = load_df_data(
        prepared_gens_ts,
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

    # Add plant names to time-series data of gens
    plants_ts = pd.merge(gens_ts, plants, how="left", on="gen_name")

    # Group gen parameters
    agg_funcs = {
        "p_mw": "sum",
        "q_max_mvar": "sum",
        "q_min_mvar": "sum",
        "v_set_kv": "mean",
        "in_service": "sum",
    }
    plants_ts = plants_ts.groupby(["plant_name", "datetime"]).agg(agg_funcs)

    # If the number of gens, which are in service, equals to zero,
    # the plant is out of service and its parameters should be undefined
    plants_ts["in_service"] = plants_ts["in_service"].astype(bool)
    value_cols = ["p_mw", "v_set_kv", "q_max_mvar", "q_min_mvar"]
    plants_ts.loc[~plants_ts["in_service"], value_cols] = np.nan

    # Return results
    if path_prepared_data:
        plants_ts.to_csv(path_prepared_data, header=True, index=True)
    else:
        return plants_ts


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 4:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython "
            "prepare_plants_ts.py path_prepared_plants path_prepared_gens_ts "
            "path_prepared_data\n"
        )

    # Run
    prepare_plants_ts(
        prepared_plants=sys.argv[1],
        prepared_gens_ts=sys.argv[2],
        path_prepared_data=sys.argv[3],
    )
