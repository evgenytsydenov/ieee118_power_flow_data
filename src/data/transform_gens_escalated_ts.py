import os
import sys
from typing import Optional

import pandas as pd

sys.path.append(os.getcwd())

from src.utils.data_loaders import load_df_data


def transform_gens_escalated_ts(
    parsed_nrel118_gens: str | pd.DataFrame,
    parsed_nrel118_escalators_ts: str | pd.DataFrame,
    path_transformed_data: Optional[str] = None,
) -> Optional[pd.DataFrame]:
    """Transform data of generators which do not have time-series information.

    Args:
        parsed_nrel118_gens: Path or dataframe with parsed generation data.
        parsed_nrel118_escalators_ts: Path or dataframe with parsed escalator data.
        path_transformed_data: Path to save transformed data.

    Returns:
        Transformed data or None if `path_transformed_data` is passed and the data
          were saved.
    """
    # Load data
    nrel118_gens = load_df_data(
        data=parsed_nrel118_gens,
        dtypes={
            "name": str,
            "max_p__mw": float,
        },
    )

    nrel118_escalators_ts = load_df_data(
        data=parsed_nrel118_escalators_ts,
        dtypes={"datetime": str, "gen_name": str, "gen_factor": float},
    )

    # Merge
    gens = nrel118_gens.merge(
        nrel118_escalators_ts, left_on="name", right_on="gen_name", how="right"
    )
    gens["gen_value"] = gens["gen_factor"] * gens["max_p__mw"]

    cols = ["datetime", "gen_name", "gen_value"]
    if path_transformed_data:
        gens[cols].to_csv(path_transformed_data, header=True, index=False)
    else:
        return gens[cols]


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 4:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython "
            "transform_gens_nonts.py path_parsed_nrel118_gens "
            "path_parsed_nrel118_escalators_ts path_transformed_data\n"
        )

    # Run
    transform_gens_escalated_ts(
        parsed_nrel118_gens=sys.argv[1],
        parsed_nrel118_escalators_ts=sys.argv[2],
        path_transformed_data=sys.argv[3],
    )
