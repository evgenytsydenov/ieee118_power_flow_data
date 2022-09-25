import sys

import numpy as np
import pandas as pd

from src.utils.data_loaders import load_df_data


def check_plants_ts(
    prepared_plants_ts: str | pd.DataFrame,
    prepared_plants: str | pd.DataFrame,
) -> None:
    """Check that plant time-series values are correct.

    Args:
        prepared_plants_ts: Path or dataframe to prepared time-series data.
        prepared_plants: Path or dataframe to prepared data.
    """
    # Load data
    plants = load_df_data(
        data=prepared_plants,
        dtypes={
            "bus_name": str,
            "plant_name": str,
        },
    )
    plants_ts = load_df_data(
        data=prepared_plants_ts,
        dtypes={
            "datetime": str,
            "plant_name": str,
            "in_service": bool,
            "q_max_mvar": float,
            "q_min_mvar": float,
            "p_mw": float,
            "v_set_kv": float,
        },
    )

    # Ensure there are no NaNs among obligatory values
    assert (
        not plants_ts[["datetime", "plant_name", "in_service"]].isna().values.any()
    ), "There are missing obligatory parameters"

    # Ensure parameters are undefined when plant is out of service
    value_cols = ["v_set_kv", "p_mw", "q_min_mvar", "q_max_mvar"]
    assert (
        plants_ts.loc[~plants_ts["in_service"], value_cols].isna().values.all()
    ), "There are value of parameters when plant is out of service"

    # Ensure there are no NaNs when plants are in service
    plants_in_service = plants_ts[plants_ts["in_service"]]
    assert (
        not plants_in_service.isna().values.any()
    ), "There are undefined parameters when plant is in service"

    # Some values should not be negative
    assert (
        plants_in_service["p_mw"] >= 0
    ).values.all(), "Some plants have negative output"
    assert (
        plants_in_service["v_set_kv"] >= 0
    ).values.all(), "Some plants have negative voltage"

    # Check reactive output
    assert (
        plants_in_service["q_min_mvar"] <= plants_in_service["q_max_mvar"]
    ).values.all(), (
        "Min level of reactive output of some plants are greater than Max level"
    )

    # Ensure there are time-series values for all plants
    plants_ts_names = plants_ts["plant_name"].unique()
    plants_names = plants["plant_name"].unique()
    assert np.isin(
        plants_names, plants_ts_names, assume_unique=True
    ).all(), "Some plants are missed in time-series data"
    assert np.isin(
        plants_ts_names, plants_names, assume_unique=True
    ).all(), "There are some unknown plants in time-series data"


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 3:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython check_plants_ts.py "
            "path_prepared_plants_ts path_prepared_plants\n"
        )

    # Run
    check_plants_ts(prepared_plants_ts=sys.argv[1], prepared_plants=sys.argv[2])
