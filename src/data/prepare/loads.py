import sys
from typing import Optional

import pandas as pd

from src.utils.data_loaders import load_df_data


def prepare_loads(
    transformed_loads: str | pd.DataFrame,
    path_prepared_data: Optional[str] = None,
) -> Optional[pd.DataFrame]:
    """Prepare final load data.

    Args:
        transformed_loads: Path or dataframe with transformed load data.
        path_prepared_data: Path to save prepared data.

    Returns:
        Prepared data or None if `path_prepared_data` is passed and the data were saved.
    """
    # Load data
    loads = load_df_data(
        data=transformed_loads,
        dtypes={"load_name": str, "bus_name": str},
    )

    # Return results
    cols = ["load_name", "bus_name"]
    loads.sort_values("load_name", inplace=True, ignore_index=True)
    if path_prepared_data:
        loads[cols].to_csv(path_prepared_data, header=True, index=False)
    else:
        return loads[cols]


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 3:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython "
            "prepare_loads.py path_transformed_loads path_prepared_data\n"
        )

    # Run
    prepare_loads(
        transformed_loads=sys.argv[1],
        path_prepared_data=sys.argv[2],
    )
