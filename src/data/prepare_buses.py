import sys
from typing import Optional

import pandas as pd

from src.utils.data_loaders import load_df_data


def prepare_buses(
    parsed_nrel118_buses: str | pd.DataFrame, path_prepared_data: Optional[str] = None
) -> Optional[pd.DataFrame]:
    """Prepare final bus data.

    Args:
        parsed_nrel118_buses: Path or dataframe to parsed data.
        path_prepared_data: Path to save prepared data.

    Returns:
        Prepared data or None if `path_prepared_data` is passed and the data were saved.
    """
    buses = load_df_data(
        data=parsed_nrel118_buses, dtypes={"bus_name": str, "region": str}
    )

    # All buses are in service
    buses["in_service"] = True

    # Add info about voltage levels
    buses["v_rated_kv"] = 138
    buses_345 = [8, 9, 10, 26, 30, 38, 63, 64, 65, 68, 81, 116]
    buses.loc[[num - 1 for num in buses_345], "v_rated_kv"] = 345

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
            "prepare_buses.py path_parsed_nrel118_buses path_prepared_data\n"
        )

    # Run
    prepare_buses(parsed_nrel118_buses=sys.argv[1], path_prepared_data=sys.argv[2])
