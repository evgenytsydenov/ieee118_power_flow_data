import sys
from typing import Optional

import pandas as pd


def parse_nrel118_lines(
    path_raw_data: str, path_parsed_data: Optional[str] = None
) -> Optional[pd.DataFrame]:
    """Fix variable names and drop unnecessary information.

    Args:
        path_raw_data: Path to raw line data from NREL-118 dataset.
        path_parsed_data: Path to save parsed data.

    Returns:
        Parsed line data or None if `path_parsed_data` is passed and the data
          were saved.
    """
    # Load raw line data
    lines = pd.read_csv(
        path_raw_data, header=0, usecols=lambda x: x not in ["Min Flow (MW)"]
    )
    lines.rename(
        columns={
            "Line Name": "name",
            "Bus from ": "from_bus",
            "Bus to": "to_bus",
            "Max Flow (MW)": "max_p_mw",
            "Reactance (p.u.)": "x_ohm",
            "Resistance (p.u.)": "r_ohm",
        },
        inplace=True,
    )
    lines.sort_values(by="name", inplace=True, ignore_index=True)

    # Unify line and bus names
    lines["name"] = "line__" + lines["name"].str.lstrip("line0")
    lines["from_bus"] = "bus__" + lines["from_bus"].str.lstrip("bus0")
    lines["to_bus"] = "bus__" + lines["to_bus"].str.lstrip("bus0")

    # Return results
    if path_parsed_data:
        lines.to_csv(path_parsed_data, header=True, index=True)
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
