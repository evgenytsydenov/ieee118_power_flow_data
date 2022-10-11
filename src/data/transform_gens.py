import sys
from typing import Optional

import pandas as pd

from definitions import PLANT_MODE
from src.utils.data_loaders import load_df_data


def transform_gens(
    parsed_nrel118_gens: str | pd.DataFrame,
    path_transformed_data: Optional[str] = None,
) -> Optional[pd.DataFrame]:
    """Group generators by bus to represent as a power plant.

    Args:
        path_transformed_data: Path to save transformed data.
        parsed_nrel118_gens: Path or dataframe with parsed generation data.

    Returns:
        Transformed data or None if `path_transformed_data` is passed
          and the data were saved.
    """
    # Load data
    gens = load_df_data(
        data=parsed_nrel118_gens,
        dtypes={
            "gen_name": str,
            "bus_name": str,
        },
    )

    # Group generators by bus
    if PLANT_MODE:
        pattern = r"^bus_(?P<index>\d+)$"
        names = gens["bus_name"].str.extract(pat=pattern, expand=True)
        gens["plant_name"] = "plant_" + names["index"]

    # Return results
    if path_transformed_data:
        gens.to_csv(path_transformed_data, header=True, index=False)
    else:
        return gens


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 3:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython "
            "transform_gens.py path_parsed_nrel118_gens path_transformed_data\n"
        )

    # Run
    transform_gens(
        parsed_nrel118_gens=sys.argv[1],
        path_transformed_data=sys.argv[2],
    )
