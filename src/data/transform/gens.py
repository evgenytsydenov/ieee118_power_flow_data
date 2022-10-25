import sys
from typing import Optional

import pandas as pd

from definitions import PLANT_MODE
from src.utils.data_loaders import load_df_data


def transform_gens(
    parsed_nrel118_gens: str | pd.DataFrame,
    prepared_buses: str | pd.DataFrame,
    path_transformed_data: Optional[str] = None,
) -> Optional[pd.DataFrame]:
    """Group generators by bus to represent as a power plant.

    Args:
        path_transformed_data: Path to save transformed data.
        prepared_buses: Path or dataframe with bus data.
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
            "max_p_mw": float,
        },
    )
    buses = load_df_data(
        data=prepared_buses,
        dtypes={"bus_name": str, "v_rated_kv": float, "is_slack": bool},
    )

    # Add bus info
    gens = gens.merge(buses, on="bus_name", how="left")

    # Group generators by bus
    cols = ["bus_name", "gen_name", "max_p_mw", "v_rated_kv", "is_slack"]
    if PLANT_MODE:
        gens.sort_values("bus_name", inplace=True, ignore_index=True)
        gens["plant_name"] = "plant_" + gens["bus_name"].str.lstrip("bus_")
        cols.insert(0, "plant_name")

    # Return results
    if path_transformed_data:
        gens[cols].to_csv(path_transformed_data, header=True, index=False)
    else:
        return gens[cols]


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 4:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython "
            "transform_gens.py path_parsed_nrel118_gens path_prepared_buses "
            "path_transformed_data\n"
        )

    # Run
    transform_gens(
        parsed_nrel118_gens=sys.argv[1],
        prepared_buses=sys.argv[2],
        path_transformed_data=sys.argv[3],
    )
