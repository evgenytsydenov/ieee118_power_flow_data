import glob
import os
import re

import pandas as pd


def load_ts_data(
    folder_path: str,
    name_pattern: str = r"Hydro (?P<name>\w+)\.csv",
    sep: str = ",",
    decimal: str = ".",
) -> pd.DataFrame:
    """Combine time-series data from multiple files.

    Args:
        decimal: Character to recognize as decimal point.
        sep: Delimiter to use.
        name_pattern: Pattern of file names to extract object number.
        folder_path: Path to folder with time-series data.

    Returns:
        Combined dataframe.
    """
    data = {}
    dates = None
    pattern = re.compile(name_pattern)
    columns = {"DATETIME", "Value", "value", "values", "Values"}
    for file in glob.glob("*", root_dir=folder_path):

        # Load current file
        file_data = pd.read_csv(
            filepath_or_buffer=os.path.join(folder_path, file),
            header=0,
            usecols=lambda col: col in columns,
            parse_dates=["DATETIME"],
            dtype={"value": float, "Value": float, "values": float, "Values": float},
            decimal=decimal,
            sep=sep,
        )

        # Change column names
        file_data.rename(
            columns={
                "DATETIME": "datetime",
                "Value": "value",
                "values": "value",
                "Values": "value",
            },
            inplace=True,
        )

        # Assume all files have the same dates
        if dates is None:
            dates = file_data["datetime"].values

        # Save to dict
        name = re.match(pattern, file).group(1)
        data[name] = file_data.loc[file_data["datetime"] == dates, "value"].values

    # Combine
    combined_data = pd.DataFrame(data={"datetime": dates, **data})
    return combined_data.sort_values(by="datetime", ignore_index=True)
