import sys
from typing import Optional

import pandas as pd

from src.utils.data_loaders import load_df_data


def prepare_plants(
    prepared_gens: str | pd.DataFrame,
    path_prepared_data: Optional[str] = None,
) -> Optional[pd.DataFrame]:
    """Group generators by bus to represent as a power plant.

    Args:
        prepared_gens: Path or dataframe with prepared generation data.
        path_prepared_data: Path to save prepared data.

    Returns:
        Prepared data or None if `path_prepared_data` is passed and the data were saved.
    """
    # Load data
    plants = load_df_data(
        data=prepared_gens,
        dtypes={
            "gen_name": str,
            "bus_name": str,
        },
    )

    # Group generators by bus
    pattern = r"^bus_(?P<index>\d+)$"
    names = plants["bus_name"].str.extract(pat=pattern, expand=True)
    plants["plant_name"] = "plant_" + names["index"]

    # Return results
    if path_prepared_data:
        plants.to_csv(path_prepared_data, header=True, index=False)
    else:
        return plants


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 3:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython "
            "prepare_plants.py path_prepared_gens path_prepared_data\n"
        )

    # Run
    prepare_plants(
        prepared_gens=sys.argv[1],
        path_prepared_data=sys.argv[2],
    )
