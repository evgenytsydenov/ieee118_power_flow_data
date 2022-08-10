import os
import sys
from typing import Optional

import pandas as pd

sys.path.append(os.getcwd())

from src.utils.common_names import gen_types
from src.utils.data_loader import load_df_data


def parse_nrel118_escalator_ts(
    raw_data: str | pd.DataFrame, path_parsed_data: Optional[str] = None
) -> Optional[pd.DataFrame]:
    """Parse raw escalators data from the NREL-118 dataset.

    Thr escalators are simple multipliers of certain generator characteristics. They
    are used to adjust a certain generation profile to seasons or other time slices.

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
            "Escalator": "name",
            "Value": "value",
            "Timeslice (month)": "month",
        },
        inplace=True,
    )

    # Unify generator names
    name_pattern = r"^(?P<plant_type>[\w\s]+)\s(?P<plant_number>\d+)$"
    names = escalators["name"].str.extract(pat=name_pattern, expand=True)
    names["plant_type"].replace(gen_types, inplace=True)
    escalators["name"] = names["plant_type"] + "_" + names["plant_number"]

    # Convert datetime
    escalators["year"] = 2024
    escalators["day"] = 1
    escalators["month"] = escalators["month"].str.lstrip("M").astype(int)
    escalators["datetime"] = pd.to_datetime(escalators[["year", "month", "day"]])

    # Return results
    cols = ["datetime", "name", "value"]
    if path_parsed_data:
        escalators[cols].to_csv(path_parsed_data, header=True, index=False)
    else:
        return escalators[cols]


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 3:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython "
            "parse_nrel118_escalator_ts.py path_raw_data path_parsed_data\n"
        )

    # Run
    parse_nrel118_escalator_ts(raw_data=sys.argv[1], path_parsed_data=sys.argv[2])
