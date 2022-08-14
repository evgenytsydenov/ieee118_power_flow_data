import sys
from typing import Optional

import numpy as np
import pandas as pd

from src.utils.data_loaders import load_df_data


def transform_loads(
    parsed_nrel118_buses: str | pd.DataFrame,
    parsed_jeas118_loads: str | pd.DataFrame,
    path_transformed_data: Optional[str] = None,
) -> Optional[pd.DataFrame]:
    """Transform load data.

    Args:
        parsed_nrel118_buses: Path or dataframe with bus data from the NREL-118 dataset.
        parsed_jeas118_loads: Path or dataframe with load data
          from the JEAS-118 dataset.
        path_transformed_data: Path to save transformed data.

    Returns:
        Transformed data or None if `path_transformed_data` is passed
          and the data were saved.
    """
    # Load data
    nrel118_buses = load_df_data(
        data=parsed_nrel118_buses,
        dtypes={"bus_name": str, "region": str, "load_participation_factor": float},
    )
    jeas118_loads = load_df_data(
        data=parsed_jeas118_loads,
        dtypes={"bus_name": str, "p__mw": float, "q__mvar": float},
    )

    # Create load dataset
    non_loads = nrel118_buses[nrel118_buses["load_participation_factor"] == 0]
    loads = nrel118_buses.drop(index=non_loads.index).reset_index(drop=True)
    loads["load_name"] = "load__" + (loads.index + 1).astype(str)

    # Calculate load tangent at each bus
    jeas118_loads["load_power_factor"] = np.cos(
        np.arctan(jeas118_loads["q__mvar"] / jeas118_loads["p__mw"])
    )
    loads = loads.merge(
        jeas118_loads[["bus_name", "load_power_factor"]], how="left", on="bus_name"
    )

    # Return results
    cols = [
        "load_name",
        "bus_name",
        "region",
        "load_participation_factor",
        "load_power_factor",
    ]
    if path_transformed_data:
        loads[cols].to_csv(path_transformed_data, header=True, index=False)
    else:
        return loads[cols]


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 4:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython "
            "transform_loads.py path_parsed_nrel118_buses path_parsed_jeas118_loads "
            "path_transformed_data\n"
        )

    # Run
    transform_loads(
        parsed_nrel118_buses=sys.argv[1],
        parsed_jeas118_loads=sys.argv[2],
        path_transformed_data=sys.argv[3],
    )
