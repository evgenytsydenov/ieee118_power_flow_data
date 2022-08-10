import os
import sys
from typing import Optional

import pandas as pd

sys.path.append(os.getcwd())

from src.utils.common_names import gen_types
from src.utils.data_loader import load_df_data


def parse_nrel118_outages_ts(
    raw_data: str | pd.DataFrame, path_parsed_data: Optional[str] = None
) -> Optional[pd.DataFrame]:
    """Parse raw data about generator outages from the NREL-118 dataset.

    Args:
        raw_data: Path or dataframe with raw data.
        path_parsed_data: Path to save parsed data.

    Returns:
        Parsed data or None if `path_parsed_data` is passed and the data were saved.
    """
    dtypes = {
        "Name": str,
        "Year": int,
        "Month": int,
        "Day": int,
        "Period": int,
        "Value": bool,
    }
    outages = load_df_data(data=raw_data, dtypes=dtypes)

    # Rename variables
    outages.rename(
        columns={
            "Name": "gen_name",
            "Value": "in_outage",
            "Period": "hour",
            "Year": "year",
            "Month": "month",
            "Day": "day",
        },
        inplace=True,
    )

    # Compute date
    outages["datetime"] = pd.to_datetime(outages[["year", "month", "day", "hour"]])

    # Unify generator names
    name_pattern = r"^(?P<plant_type>[\w\s]+)\s(?P<plant_number>\d+)$"
    names = outages["gen_name"].str.extract(pat=name_pattern, expand=True)
    names["plant_type"].replace(gen_types, inplace=True)
    outages["gen_name"] = (
        names["plant_type"] + "_" + names["plant_number"].str.lstrip("0")
    )

    # Return results
    cols = ["datetime", "gen_name", "in_outage"]
    if path_parsed_data:
        outages[cols].to_csv(path_parsed_data, header=True, index=False)
    else:
        return outages[cols]


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 3:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython "
            "parse_nrel118_outages_ts.py path_raw_data path_parsed_data\n"
        )

    # Run
    parse_nrel118_outages_ts(raw_data=sys.argv[1], path_parsed_data=sys.argv[2])
