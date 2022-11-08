import sys
from typing import Optional

import pandas as pd

from src.utils.converters import docx_to_pandas


def parse_jeas118_trafos(
    raw_data: str | pd.DataFrame, path_parsed_data: Optional[str] = None
) -> Optional[pd.DataFrame]:
    """Parse raw transformer data from the JEAS-118 dataset.

    Args:
        raw_data: Path or dataframe with raw data.
        path_parsed_data: Path to save parsed data.

    Returns:
        Parsed data or None if `path_parsed_data` is passed and the data were saved.
    """
    dtypes = {
        "From Bus": str,
        "To\nBus": str,
        "Circuit ID": int,
        "Tap Initial": float,
    }
    cols = dtypes.keys()
    if isinstance(raw_data, str):
        trafos = docx_to_pandas(path_docx=raw_data, table_num=4, header_num=1)
        trafos = trafos[cols].astype(dtypes)
    else:
        trafos = raw_data[cols].astype(dtypes)

    # Rename variables
    trafos.rename(
        columns={
            "From Bus": "from_bus",
            "To\nBus": "to_bus",
            "Circuit ID": "parallel",
            "Tap Initial": "trafo_ratio_rel",
        },
        inplace=True,
    )

    # Change trafo and bus names
    trafos["from_bus"] = "bus_" + trafos["from_bus"].str.zfill(3)
    trafos["to_bus"] = "bus_" + trafos["to_bus"].str.zfill(3)

    # Return results
    trafos.sort_values(
        by=["from_bus", "to_bus", "parallel"], ignore_index=True, inplace=True
    )
    if path_parsed_data:
        trafos.to_csv(path_parsed_data, header=True, index=False)
    else:
        return trafos


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 3:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython "
            "parse_jeas118_trafos.py path_raw_jeas118 path_parsed_data\n"
        )

    # Run
    parse_jeas118_trafos(raw_data=sys.argv[1], path_parsed_data=sys.argv[2])
