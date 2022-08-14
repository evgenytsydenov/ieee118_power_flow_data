import os
import sys
from typing import Optional

import pandas as pd

sys.path.append(os.getcwd())

from src.utils.data_loaders import load_df_data


def parse_nrel118_buses(
    raw_data: str | pd.DataFrame, path_parsed_data: Optional[str] = None
) -> Optional[pd.DataFrame]:
    """Parse raw bus data from the NREL-118 dataset.

    Args:
        raw_data: Path or dataframe with raw data.
        path_parsed_data: Path to save parsed data.

    Returns:
        Parsed data or None if `path_parsed_data` is passed and the data were saved.
    """
    dtypes = {"Bus Name": str, "Region": str, "Load Participation Factor": float}
    buses = load_df_data(data=raw_data, dtypes=dtypes)

    # Load raw bus data
    buses.rename(
        columns={
            "Bus Name": "bus_name",
            "Region": "region",
            "Load Participation Factor": "load_participation_factor",
        },
        inplace=True,
    )
    buses.sort_values(by="bus_name", inplace=True, ignore_index=True)

    # Unify bus names
    buses["bus_name"] = "bus__" + buses["bus_name"].str.lstrip("bus0")

    # Convert regions to lowercase
    buses["region"] = buses["region"].str.lower()

    # Return results
    if path_parsed_data:
        buses.to_csv(path_parsed_data, header=True, index=False)
    else:
        return buses


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 3:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython "
            "parse_nrel118_buses.py path_raw_nrel118_buses path_parsed_data\n"
        )

    # Run
    parse_nrel118_buses(raw_data=sys.argv[1], path_parsed_data=sys.argv[2])
