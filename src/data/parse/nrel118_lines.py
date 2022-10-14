import sys
from typing import Optional

import pandas as pd

from src.utils.data_loaders import load_df_data


def parse_nrel118_lines(
    raw_data: str | pd.DataFrame, path_parsed_data: Optional[str] = None
) -> Optional[pd.DataFrame]:
    """Parse raw line data from the NREL-118 dataset.

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
    lines = load_df_data(data=raw_data, dtypes=dtypes)

    # Rename variables
    lines.rename(
        columns={
            "Line Name": "branch_name",
            "Bus from ": "from_bus",
            "Bus to": "to_bus",
            "Max Flow (MW)": "max_p_mw",
            "Reactance (p.u.)": "x_pu",
            "Resistance (p.u.)": "r_pu",
        },
        inplace=True,
    )

    # Unify line and bus names
    lines["branch_name"] = "branch_" + lines["branch_name"].str.lstrip(
        "line"
    ).str.zfill(3)
    lines["from_bus"] = "bus_" + lines["from_bus"].str.lstrip("bus").str.zfill(3)
    lines["to_bus"] = "bus_" + lines["to_bus"].str.lstrip("bus").str.zfill(3)

    # Return results
    lines.sort_values(by="branch_name", inplace=True, ignore_index=True)
    if path_parsed_data:
        lines.to_csv(path_parsed_data, header=True, index=False)
    else:
        return lines


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 3:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython "
            "parse_nrel118_lines.py path_raw_nrel118_lines path_parsed_data\n"
        )

    # Run
    parse_nrel118_lines(raw_data=sys.argv[1], path_parsed_data=sys.argv[2])
