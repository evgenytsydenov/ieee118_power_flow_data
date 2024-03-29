import sys
from typing import Optional

import pandas as pd

from definitions import DATE_FORMAT, GEN_TYPES
from src.utils.data_loaders import load_df_data


def parse_nrel118_outages_ts(
    raw_data: str | pd.DataFrame, path_parsed_data: Optional[str] = None
) -> Optional[pd.DataFrame]:
    """Parse raw time-series data of generator outages from the NREL-118 dataset.

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
    outages["datetime"] = pd.to_datetime(
        outages[["year", "month", "day", "hour"]]
    ).dt.strftime(DATE_FORMAT)

    # Unify generator names
    name_pattern = r"^(?P<gen_type>[\w\s]+)\s(?P<gen_number>\d+)$"
    names = outages["gen_name"].str.extract(pat=name_pattern, expand=True)
    names["gen_type"].replace(GEN_TYPES, inplace=True)
    outages["gen_name"] = names["gen_type"] + "_" + names["gen_number"].str.zfill(3)

    # Return results
    outages.sort_values(["datetime", "gen_name"], inplace=True, ignore_index=True)
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
            "parse_nrel118_outages_ts.py path_raw_nrel118_outages_ts path_parsed_data\n"
        )

    # Run
    parse_nrel118_outages_ts(raw_data=sys.argv[1], path_parsed_data=sys.argv[2])
