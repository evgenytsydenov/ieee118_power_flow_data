import glob
import os
import re
from typing import Optional

import pandas as pd


def load_df_data(
    data: str | pd.DataFrame, dtypes: dict, nrows: Optional[int] = None
) -> pd.DataFrame:
    """Load dataframes and convert data to the proper types.

    Args:
        dtypes: Path for each column
        data: Path or dataframe with data.
        nrows: Number of first rows to return.

    Returns:
        Loaded data as a dataframe.
    """
    cols = dtypes.keys()
    if isinstance(data, str):
        return pd.read_csv(data, header=0, usecols=cols, dtype=dtypes, nrows=nrows)
    result = data if nrows is None else data.head(nrows)
    return result[cols].astype(dtypes)


def load_ts_data(
    folder_path: str, name_pattern: str = r"Hydro (?P<name>\w+)\.csv"
) -> pd.DataFrame:
    """Combine time-series data from multiple files.

    Args:
        name_pattern: Pattern of file names to extract object number.
        folder_path: Path to folder with time-series data.

    Returns:
        Combined dataframe.
    """
    data = {}
    dates = None
    pattern = re.compile(name_pattern)
    for file in glob.glob("*", root_dir=folder_path):

        # Load current file
        file_data = pd.read_csv(
            filepath_or_buffer=os.path.join(folder_path, file),
            header=0,
            usecols=["DATETIME", "value"],
            parse_dates=["DATETIME"],
            dtype={"value": float},
        )

        # Change column names
        file_data.rename(columns={"DATETIME": "datetime"}, inplace=True)

        # Assume all files have the same dates
        if dates is None:
            dates = file_data["datetime"].values

        # Save to dict
        name = re.match(pattern, file).group(1)
        data[name] = file_data.loc[file_data["datetime"] == dates, "value"].values

    # Combine
    combined_data = pd.DataFrame(data={"datetime": dates, **data})
    return combined_data.sort_values(by="datetime", ignore_index=True)
