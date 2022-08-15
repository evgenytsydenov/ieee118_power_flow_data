import sys
from typing import Optional

import pandas as pd

from definitions import DATE_FORMAT, GEN_TYPES
from src.utils.data_loaders import load_ts_data


def parse_nrel118_winds_ts(
    raw_data: str, path_parsed_data: Optional[str] = None
) -> Optional[pd.DataFrame]:
    """Parse raw time-series data of wind plants from the NREL-118 dataset.

    Args:
        raw_data: Path to the raw data.
        path_parsed_data: Path to save parsed data.

    Returns:
        Parsed data or None if `path_parsed_data` is passed and the data were saved.
    """
    # Load data
    name_pattern = r"Wind(?P<name>\d+)RT\.csv"
    wind_ts = load_ts_data(folder_path=raw_data, name_pattern=name_pattern)

    # Change column names
    wind_ts.rename(columns={"name": "gen_name", "value": "p_mw"}, inplace=True)
    wind_ts["gen_name"] = GEN_TYPES["Wind"] + "_" + wind_ts["gen_name"]

    # Unify date format
    wind_ts["datetime"] = wind_ts["datetime"].dt.strftime(DATE_FORMAT)

    # Return results
    if path_parsed_data:
        wind_ts.to_csv(path_parsed_data, header=True, index=False)
    else:
        return wind_ts


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 3:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython "
            "parse_nrel118_winds_ts.py path_raw_nrel118_winds_ts path_parsed_data\n"
        )

    # Run
    parse_nrel118_winds_ts(raw_data=sys.argv[1], path_parsed_data=sys.argv[2])
