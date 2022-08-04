import os
import sys
from typing import Optional

import pandas as pd

sys.path.append(os.getcwd())

from src.utils.data_loader import load_df_data


def parse_nrel118_lines(
    raw_data: str | pd.DataFrame, path_parsed_data: Optional[str] = None
) -> Optional[pd.DataFrame]:
    """Parse raw line data from NREL-118 dataset.

    Args:
        raw_data: Path or dataframe with raw data.
        path_parsed_data: Path to save parsed data.

    Returns:
        Parsed data or None if `path_parsed_data` is passed and the data were saved.
    """
    dtypes = {
        "Line Name": str,
        "Bus from ": str,
        "Bus to": str,
        "Max Flow (MW)": float,
        "Reactance (p.u.)": float,
        "Resistance (p.u.)": float,
    }
    lines = load_df_data(raw_data, dtypes)

    # Rename variables
    lines.rename(
        columns={
            "Line Name": "name",
            "Bus from ": "from_bus",
            "Bus to": "to_bus",
            "Max Flow (MW)": "max_p__mw",
            "Reactance (p.u.)": "x__pu",
            "Resistance (p.u.)": "r__pu",
        },
        inplace=True,
    )
    lines.sort_values(by="name", inplace=True, ignore_index=True)

    # Unify line and bus names
    lines["name"] = "branch_" + lines["name"].str.lstrip("line0")
    lines["from_bus"] = "bus_" + lines["from_bus"].str.lstrip("bus0")
    lines["to_bus"] = "bus_" + lines["to_bus"].str.lstrip("bus0")

    # Return results
    if path_parsed_data:
        lines.to_csv(path_parsed_data, header=True, index=False)
    else:
        return lines


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 3:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython "
            "parse_nrel118_lines.py path_raw_data path_parsed_data\n"
        )

    # Run
    parse_nrel118_lines(raw_data=sys.argv[1], path_parsed_data=sys.argv[2])
