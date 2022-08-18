import sys

import pandas as pd

from src.utils.data_loaders import load_df_data


def check_loads(prepared_loads: str | pd.DataFrame) -> None:
    """Check that load parameters are correct.

    Args:
        prepared_loads: Path or dataframe to prepared data.
    """
    # Load data
    loads = load_df_data(
        data=prepared_loads,
        dtypes={
            "bus_name": str,
            "load_name": str,
        },
    )

    # Ensure there are no NaNs
    assert not loads.isna().values.any(), "There are NaNs in the dataset"

    # Ensure load names are unique
    assert loads["load_name"].is_unique, "There are duplicated load names"

    # Ensure there is only one load per bus
    assert loads["bus_name"].is_unique, "There are several loads at one bus"


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 2:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython check_loads.py path_prepared_loads\n"
        )

    # Run
    check_loads(prepared_loads=sys.argv[1])
