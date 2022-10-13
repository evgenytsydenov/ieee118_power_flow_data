import sys
from typing import Optional

import pandas as pd

from definitions import DATE_FORMAT, GEN_TYPES
from src.utils.data_loaders import load_df_data


def parse_nrel118_escalators_ts(
    raw_data: str | pd.DataFrame, path_parsed_data: Optional[str] = None
) -> Optional[pd.DataFrame]:
    """Parse raw escalators data from the NREL-118 dataset.

    Args:
        raw_data: Path or dataframe with raw data.
        path_parsed_data: Path to save parsed data.

    Returns:
        Parsed data or None if `path_parsed_data` is passed and the data were saved.
    """
    dtypes = {"Escalator": str, "Value": float, "Timeslice (month)": str}
    escalators = load_df_data(data=raw_data, dtypes=dtypes)

    # Rename variables
    escalators.rename(
        columns={
            "Escalator": "gen_name",
            "Value": "escalator_ratio",
            "Timeslice (month)": "month",
        },
        inplace=True,
    )

    # Unify generator names
    name_pattern = r"^(?P<gen_type>[\w\s]+)\s(?P<gen_number>\d+)$"
    names = escalators["gen_name"].str.extract(pat=name_pattern, expand=True)
    names["gen_type"].replace(GEN_TYPES, inplace=True)
    escalators["gen_name"] = (
        names["gen_type"] + "_" + names["gen_number"].str.lstrip("0")
    )

    # Convert datetime
    escalators["year"] = 2024
    escalators["day"] = 1
    escalators["month"] = escalators["month"].str.lstrip("M").astype(int)
    escalators["datetime"] = pd.to_datetime(
        escalators[["year", "month", "day"]]
    ).dt.strftime(DATE_FORMAT)

    # Return results
    cols = ["datetime", "gen_name", "escalator_ratio"]
    if path_parsed_data:
        escalators[cols].to_csv(path_parsed_data, header=True, index=False)
    else:
        return escalators[cols]


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 3:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython "
            "parse_nrel118_escalators_ts.py path_raw_nrel118_escalators "
            "path_parsed_data\n"
        )

    # Run
    parse_nrel118_escalators_ts(raw_data=sys.argv[1], path_parsed_data=sys.argv[2])
