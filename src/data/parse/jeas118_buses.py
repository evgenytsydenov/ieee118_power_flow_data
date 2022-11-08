import sys
from typing import Optional

import pandas as pd

from src.utils.converters import docx_to_pandas


def parse_jeas118_buses(
    raw_data: str | pd.DataFrame, path_parsed_data: Optional[str] = None
) -> Optional[pd.DataFrame]:
    """Parse raw bus data from the JEAS-118 dataset.

    Args:
        raw_data: Path or dataframe with raw data.
        path_parsed_data: Path to save parsed data.

    Returns:
        Parsed data or None if `path_parsed_data` is passed and the data were saved.
    """
    dtypes = {"Bus No.": str, "Voltage-Max (pu)": float, "Voltage-Min (pu)": float}
    cols = dtypes.keys()
    if isinstance(raw_data, str):
        buses = docx_to_pandas(path_docx=raw_data, table_num=2, header_num=1)
        buses = buses[cols].astype(dtypes)
    else:
        buses = raw_data[cols].astype(dtypes)

    # Rename variables
    buses.rename(
        columns={
            "Bus No.": "bus_name",
            "Voltage-Max (pu)": "max_v_pu",
            "Voltage-Min (pu)": "min_v_pu",
        },
        inplace=True,
    )

    # Change bus names
    buses["bus_name"] = "bus_" + buses["bus_name"].str.zfill(3)

    # Return results
    buses.sort_values(by="bus_name", inplace=True, ignore_index=True)
    if path_parsed_data:
        buses.to_csv(path_parsed_data, header=True, index=False)
    else:
        return buses


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 3:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython "
            "parse_jeas118_buses.py path_raw_jeas118 path_parsed_data\n"
        )

    # Run
    parse_jeas118_buses(raw_data=sys.argv[1], path_parsed_data=sys.argv[2])
