import sys
from typing import Optional

import pandas as pd

from src.utils.data_loaders import load_ts_data


def parse_nrel118_hydros_ts(
    raw_data: str, path_parsed_data: Optional[str] = None
) -> Optional[pd.DataFrame]:
    """Parse raw time-series data of hydro plants from the NREL-118 dataset.

    Args:
        raw_data: Path to the raw data.
        path_parsed_data: Path to save parsed data.

    Returns:
        Parsed data or None if `path_parsed_data` is passed and the data were saved.
    """
    # Load data
    name_pattern = r"Hydro (?P<name>\d+)\.csv"
    hydro_ts = load_ts_data(folder_path=raw_data, name_pattern=name_pattern)

    # Change column names
    hydro_ts.rename(columns={"name": "gen_name", "value": "p__mw"}, inplace=True)
    hydro_ts["gen_name"] = "hydro__" + hydro_ts["gen_name"]

    # Return results
    if path_parsed_data:
        hydro_ts.to_csv(path_parsed_data, header=True, index=False)
    else:
        return hydro_ts


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 3:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython "
            "parse_nrel118_hydros_ts.py path_raw_nrel118_hydro_ts path_parsed_data\n"
        )

    # Run
    parse_nrel118_hydros_ts(raw_data=sys.argv[1], path_parsed_data=sys.argv[2])
