import os
import sys
from typing import Optional

import pandas as pd

sys.path.append(os.getcwd())

from src.utils.data_loader import load_ts_data


def parse_nrel118_load_ts(
    raw_data: str, path_parsed_data: Optional[str] = None
) -> Optional[pd.DataFrame]:
    """Parse time-series data about loads from the NREL-118 dataset.

    Args:
        raw_data: Path to the raw data.
        path_parsed_data: Path to save parsed data.

    Returns:
        Parsed data or None if `path_parsed_data` is passed and the data were saved.
    """
    # Load data
    name_pattern = r"Load(?P<name>\w+)RT\.csv"
    load_ts = load_ts_data(raw_data, name_pattern)

    # Change column names
    load_ts.columns = [col.lower() for col in load_ts.columns]

    # Return results
    if path_parsed_data:
        load_ts.to_csv(path_parsed_data, header=True, index=False)
    else:
        return load_ts


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 3:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython "
            "parse_nrel118_load_ts.py path_raw_data path_parsed_data\n"
        )

    # Run
    parse_nrel118_load_ts(raw_data=sys.argv[1], path_parsed_data=sys.argv[2])
