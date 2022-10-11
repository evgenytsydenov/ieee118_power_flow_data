import sys

import pandas as pd

from definitions import PLANT_MODE
from src.utils.data_loaders import load_df_data


def check_gens(prepared_gens: str | pd.DataFrame) -> None:
    """Check that generator parameters are correct.

    Args:
        prepared_gens: Path or dataframe to prepared data.
    """
    # Load data
    gens = load_df_data(data=prepared_gens, dtypes={"bus_name": str, "gen_name": str})

    # Ensure there are no NaNs
    assert not gens.isna().values.any(), "There are NaNs in the dataset"

    # Ensure gen names are unique
    assert gens["gen_name"].is_unique, "There are duplicated gen names"

    # Ensure there is only one plant per bus
    if PLANT_MODE:
        assert gens["bus_name"].is_unique, "Some bus contains several plants"


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 2:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython check_gens.py path_prepared_gens\n"
        )

    # Run
    check_gens(prepared_gens=sys.argv[1])
