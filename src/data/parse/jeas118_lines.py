import sys
from typing import Optional

import pandas as pd

from src.utils.converters import docx_to_pandas


def parse_jeas118_lines(
    raw_data: str | pd.DataFrame, path_parsed_data: Optional[str] = None
) -> Optional[pd.DataFrame]:
    """Parse raw line data from the JEAS-118 dataset.

    Args:
        raw_data: Path or dataframe with raw data.
        path_parsed_data: Path to save parsed data.

    Returns:
        Parsed data or None if `path_parsed_data` is passed and the data were saved.
    """
    dtypes = {
        "From Bus": str,
        "To Bus": str,
        "Circuit ID": int,
        "B (pu)": float,
    }
    cols = dtypes.keys()
    if isinstance(raw_data, str):
        lines = docx_to_pandas(path_docx=raw_data, table_num=3, header_num=1)
        lines = lines[cols].astype(dtypes)
    else:
        lines = raw_data[cols].astype(dtypes)

    # Rename variables
    lines.rename(
        columns={
            "From Bus": "from_bus",
            "To Bus": "to_bus",
            "Circuit ID": "parallel",
            "B (pu)": "b_pu",
        },
        inplace=True,
    )

    # Change branch and bus names
    lines["from_bus"] = "bus_" + lines["from_bus"].str.zfill(3)
    lines["to_bus"] = "bus_" + lines["to_bus"].str.zfill(3)

    # Return results
    lines.sort_values(
        by=["from_bus", "to_bus", "parallel"], ignore_index=True, inplace=True
    )
    if path_parsed_data:
        lines.to_csv(path_parsed_data, header=True, index=False)
    else:
        return lines


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 3:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython "
            "parse_jeas118_lines.py path_raw_jeas118 path_parsed_data\n"
        )

    # Run
    parse_jeas118_lines(raw_data=sys.argv[1], path_parsed_data=sys.argv[2])
