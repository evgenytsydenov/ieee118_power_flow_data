import sys
from typing import Optional

import pandas as pd

from definitions import PLANT_MODE
from src.utils.data_loaders import load_df_data


def prepare_gens(
    transformed_gens: str | pd.DataFrame,
    path_prepared_data: Optional[str] = None,
) -> Optional[pd.DataFrame]:
    """Prepare final generation data.

    Args:
        transformed_gens: Path or dataframe with transformed generation data.
        path_prepared_data: Path to save prepared data.

    Returns:
        Prepared data or None if `path_prepared_data` is passed and the data were saved.
    """
    # Load data
    dtypes = {"gen_name": str, "bus_name": str}
    if PLANT_MODE:
        dtypes["plant_name"] = str
    gens = load_df_data(data=transformed_gens, dtypes=dtypes)

    # Change names for consistency in further scripts
    if PLANT_MODE:
        gens.drop(columns=["gen_name"], inplace=True)
        gens.drop_duplicates(["bus_name", "plant_name"], inplace=True)
        gens.rename(columns={"plant_name": "gen_name"}, inplace=True)

    # Return results
    cols = ["gen_name", "bus_name"]
    gens.sort_values("gen_name", inplace=True, ignore_index=True)
    if path_prepared_data:
        gens[cols].to_csv(path_prepared_data, header=True, index=False)
    else:
        return gens[cols]


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 3:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython "
            "prepare_gens.py path_transformed_gens path_prepared_data\n"
        )

    # Run
    prepare_gens(transformed_gens=sys.argv[1], path_prepared_data=sys.argv[2])