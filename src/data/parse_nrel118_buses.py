import sys
from typing import Optional

import pandas as pd


def parse_nrel118_buses(
    path_raw_data: str, path_parsed_data: Optional[str] = None
) -> Optional[pd.DataFrame]:
    """Fix bus names and drop unnecessary information.

    Args:
        path_raw_data: Path to raw bus data from NREL-118 dataset.
        path_parsed_data: Path to save parsed data.

    Returns:
        Parsed bus data or None if `path_parsed_data` is passed and the data were saved.
    """
    # Load raw bus data
    buses = pd.read_csv(path_raw_data, header=0, usecols=["Bus Name", "Region"])
    buses.rename(columns={"Bus Name": "name", "Region": "region"}, inplace=True)
    buses.sort_values(by="name", inplace=True, ignore_index=True)

    # Unify bus names
    buses["name"] = "bus__" + buses["name"].str.lstrip("bus0")

    # Return results
    if path_parsed_data:
        buses.to_csv(path_parsed_data, header=True, index=True)
    else:
        return buses


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 3:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython "
            "parse_nrel118_buses.py path_raw_data path_parsed_data\n"
        )

    # Run
    path_raw_data = sys.argv[1]
    path_parsed_data = sys.argv[2]
    parse_nrel118_buses(path_raw_data, path_parsed_data)
