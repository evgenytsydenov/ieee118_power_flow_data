import sys
from typing import Optional

import pandas as pd


def prepare_buses(
    parsed_data: str | pd.DataFrame, path_prepared_data: Optional[str] = None
) -> Optional[pd.DataFrame]:
    """Prepare final bus data.

    Args:
        parsed_data: Path or dataframe to parsed data.
        path_prepared_data: Path to save prepared data.

    Returns:
        Prepared data or None if `path_prepared_data` is passed and the data were saved.
    """
    dtypes = {"name": str, "region": str}
    cols = dtypes.keys()
    if isinstance(parsed_data, str):
        buses = pd.read_csv(parsed_data, header=0, usecols=cols, dtype=dtypes)
    else:
        buses = parsed_data[cols].astype(dtypes)

    # All buses are in service
    buses["in_service"] = True

    # Add info about voltage levels
    buses["v_rated__kv"] = 138
    buses_345 = [8, 9, 10, 26, 30, 38, 63, 64, 65, 68, 81, 116]
    buses.loc[[num - 1 for num in buses_345], "v_rated__kv"] = 345

    # Return results
    if path_prepared_data:
        buses.to_csv(path_prepared_data, header=True, index=False)
    else:
        return buses


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 3:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython "
            "prepare_buses.py path_parsed_data path_prepared_data\n"
        )

    # Run
    prepare_buses(parsed_data=sys.argv[1], path_prepared_data=sys.argv[2])
