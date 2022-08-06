import os
import sys
from typing import Optional

import numpy as np
import pandas as pd

sys.path.append(os.getcwd())

from src.utils.data_loader import load_df_data


def prepare_loads(
    transformed_loads: str | pd.DataFrame,
    parsed_nrel118_loads_ts: str | pd.DataFrame,
    path_prepared_data: Optional[str] = None,
) -> Optional[pd.DataFrame]:
    """Prepare final load data.

    Args:
        transformed_loads: Path or dataframe with transformed load data.
        parsed_nrel118_loads_ts: Path or dataframe with time-series load data
          from the NREL-118 dataset.
        path_prepared_data: Path to save prepared data.

    Returns:
        Prepared data or None if `path_prepared_data` is passed and the data were saved.
    """
    # Load data
    interim_loads = load_df_data(
        transformed_loads,
        {
            "name": str,
            "bus_name": str,
            "region": str,
            "load_participation_factor": float,
            "load_power_factor": float,
        },
    )
    nrel118_loads_ts = load_df_data(
        parsed_nrel118_loads_ts, {"r1": float, "r2": float, "r3": float}, 1
    )

    # Calculate active and reactive load at each bus
    region_loads = nrel118_loads_ts.squeeze()
    region_loads.name = "region_load"
    loads = interim_loads.merge(
        region_loads, left_on="region", right_index=True, how="left"
    )
    loads["p__mw"] = loads["region_load"] * loads["load_participation_factor"]
    loads["q__mvar"] = loads["p__mw"] * np.tan(np.arccos(loads["load_power_factor"]))

    # Return results
    cols = ["name", "bus_name", "p__mw", "q__mvar"]
    if path_prepared_data:
        loads[cols].to_csv(path_prepared_data, header=True, index=False)
    else:
        return loads[cols]


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 4:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython "
            "prepare_loads.py path_transformed_loads path_parsed_nrel118_loads_ts "
            "path_prepared_data\n"
        )

    # Run
    prepare_loads(
        transformed_loads=sys.argv[1],
        parsed_nrel118_loads_ts=sys.argv[2],
        path_prepared_data=sys.argv[3],
    )
