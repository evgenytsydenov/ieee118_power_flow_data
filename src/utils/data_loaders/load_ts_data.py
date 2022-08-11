import glob
import os
import re

import pandas as pd

from definitions import DATE_FORMAT


def load_ts_data(
    folder_path: str,
    name_pattern: str = r"(?P<name>Hydro\s\d+)\.csv",
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
    data = []
    pattern = re.compile(name_pattern)
    for file in glob.glob("*", root_dir=folder_path):
        # Load current file
        file_data = pd.read_csv(
            filepath_or_buffer=os.path.join(folder_path, file),
            header=0,
            parse_dates=["DATETIME"],
            decimal=decimal,
            sep=sep,
        )

        # Change column names
        file_data.rename(
            columns=lambda col: re.sub("[V|v]alues?", "value", col),
            inplace=True,
        )
        file_data.rename(columns={"DATETIME": "datetime"}, inplace=True)

        # Save
        file_data["name"] = re.match(pattern, file).group(1)
        data.append(file_data)

    # Combine
    result = pd.concat(data).sort_values(by="datetime", ignore_index=True)
    result["datetime"] = result["datetime"].dt.strftime(DATE_FORMAT)
    return result[["datetime", "name", "value"]]
