import sys

import pandas as pd

from src.utils.data_loaders import load_df_data


def check_plants(prepared_plants: str | pd.DataFrame) -> None:
    """Check that plant parameters are correct.

    Args:
        prepared_plants: Path or dataframe to prepared data.
    """
    # Load data
    plants = load_df_data(
        data=prepared_plants,
        dtypes={
            "bus_name": str,
            "gen_name": str,
            "plant_name": str,
        },
    )

    # Ensure there are no NaNs
    assert not plants.isna().values.any(), "There are NaNs in the dataset"

    # Ensure gen names are unique
    plants.drop_duplicates(["bus_name", "plant_name"], inplace=True)
    assert (
        plants["bus_name"].is_unique and plants["plant_name"].is_unique
    ), "Some plants are located in several buses or some bus contains several plants"


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 2:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython "
            "check_plants.py path_prepared_plants\n"
        )

    # Run
    check_plants(prepared_plants=sys.argv[1])
