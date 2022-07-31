import sys
from typing import Optional

import pandas as pd


def parse_nrel118_lines(
    raw_data: str | pd.DataFrame, path_parsed_data: Optional[str] = None
) -> Optional[pd.DataFrame]:
    """Fix variable names and drop unnecessary information.

    Args:
        raw_data: Path or dataframe with raw line data from NREL-118 dataset.
        path_parsed_data: Path to save parsed data.

    Returns:
        Parsed line data or None if `path_parsed_data` is passed and the data
          were saved.
    """
    if isinstance(raw_data, str):
        lines = pd.read_csv(
            raw_data, header=0, usecols=lambda x: x not in ["Min Flow (MW)"]
        )
    else:
        lines = raw_data.drop(columns=["Min Flow (MW)"])

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
    path_raw_data = sys.argv[1]
    path_parsed_data = sys.argv[2]
    parse_nrel118_lines(path_raw_data, path_parsed_data)
