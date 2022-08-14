import os
import sys
from typing import Optional

import pandas as pd

sys.path.append(os.getcwd())

from src.utils.data_loaders import load_df_data


def prepare_gens(
    parsed_data: str | pd.DataFrame,
    path_prepared_data: Optional[str] = None,
) -> Optional[pd.DataFrame]:
    """Prepare final generation data.

    Args:
        parsed_data: Path or dataframe with parsed generation data.
        path_prepared_data: Path to save prepared data.

    Returns:
        Prepared data or None if `path_prepared_data` is passed and the data were saved.
    """
    # Load data
    gens = load_df_data(
        data=parsed_data,
        dtypes={
            "name": str,
            "bus_name": str,
        },
    )

    # Return results
    if path_prepared_data:
        gens.to_csv(path_prepared_data, header=True, index=False)
    else:
        return gens


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 3:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython "
            "prepare_gens.py path_parsed_gens path_prepared_data\n"
        )

    # Run
    prepare_gens(
        parsed_data=sys.argv[1],
        path_prepared_data=sys.argv[2],
    )
