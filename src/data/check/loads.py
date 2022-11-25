import sys

import pandas as pd

from src.utils.data_loaders import load_df_data


def check_loads(
    prepared_loads: str | pd.DataFrame, prepared_buses: str | pd.DataFrame
) -> None:
    """Check that load parameters are correct.

    Args:
        prepared_buses: Path or dataframe to prepared data.
        prepared_loads: Path or dataframe to prepared data.

    Raises:
        AssertionError: Some check fails.
    """
    # Load data
    loads = load_df_data(
        data=prepared_loads, dtypes={"bus_name": str, "load_name": str}
    )
    buses = load_df_data(data=prepared_buses, dtypes={"bus_name": str})

    # Ensure there are no NaNs
    assert not loads.isna().values.any(), "There are NaNs in the dataset"

    # Ensure load names are unique
    assert loads["load_name"].is_unique, "There are duplicated load names"

    # Ensure all bus names are in the bus dataset
    assert (
        loads["bus_name"].isin(buses["bus_name"]).all()
    ), "There are unknown bus names"

    # Ensure there is only one load per bus
    assert loads["bus_name"].is_unique, "There are several loads at one bus"


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 3:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython check_loads.py path_prepared_loads "
            "path_prepared_buses\n"
        )

    # Run
    check_loads(prepared_loads=sys.argv[1], prepared_buses=sys.argv[2])
