import sys

import pandas as pd

from definitions import PLANT_MODE
from src.utils.data_loaders import load_df_data


def check_gens(
    prepared_gens: str | pd.DataFrame, prepared_buses: str | pd.DataFrame
) -> None:
    """Check that generator parameters are correct.

    Args:
        prepared_buses: Path or dataframe to prepared data.
        prepared_gens: Path or dataframe to prepared data.
    """
    # Load data
    gens = load_df_data(
        data=prepared_gens, dtypes={"bus_name": str, "gen_name": str, "max_p_mw": float}
    )
    buses = load_df_data(data=prepared_buses, dtypes={"bus_name": str})

    # Ensure there are no NaNs
    assert not gens.isna().values.any(), "There are NaNs in the dataset"

    # Ensure gen names are unique
    assert gens["gen_name"].is_unique, "There are duplicated gen names"

    # Ensure all bus names are in bus dataset
    assert gens["bus_name"].isin(buses["bus_name"]).all(), "There are unknown bus names"

    # Ensure max output is not negative
    assert (gens["max_p_mw"] >= 0).all(), "There are negative max outputs"

    # Ensure there is only one plant per bus
    if PLANT_MODE:
        assert gens["bus_name"].is_unique, "Some bus contains several plants"


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 3:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython check_gens.py path_prepared_gens "
            "path_prepared_buses\n"
        )

    # Run
    check_gens(prepared_gens=sys.argv[1], prepared_buses=sys.argv[2])
