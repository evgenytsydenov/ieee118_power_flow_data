import sys
from datetime import datetime
from typing import Optional

import pandas as pd

from definitions import DATE_FORMAT
from src.utils.data_loaders import load_df_data


def transform_gens_escalated_ts(
    transformed_gens: str | pd.DataFrame,
    parsed_nrel118_escalators_ts: str | pd.DataFrame,
    path_transformed_data: Optional[str] = None,
) -> Optional[pd.DataFrame]:
    """Transform data of generators which have info about escalation factor.

    Args:
        transformed_gens: Path or dataframe with transformed generation data.
        parsed_nrel118_escalators_ts: Path or dataframe with parsed escalator data.
        path_transformed_data: Path to save transformed data.

    Returns:
        Transformed data or None if `path_transformed_data` is passed and the data
          were saved.
    """
    # Load data
    gens = load_df_data(
        data=transformed_gens,
        dtypes={
            "gen_name": str,
            "max_p_mw": float,
            "min_p_mw": float,
        },
    )
    nrel118_escalators_ts = load_df_data(
        data=parsed_nrel118_escalators_ts,
        dtypes={"datetime": str, "gen_name": str, "escalator_ratio": float},
    )

    # Generators which do not have escalators
    non_escalated = ~gens["gen_name"].isin(nrel118_escalators_ts["gen_name"])
    gens_non_escalated = pd.DataFrame(
        data={
            "gen_name": gens.loc[non_escalated, "gen_name"].values,
            "datetime": datetime(2024, 1, 1, 0, 0, 0).strftime(DATE_FORMAT),
            "escalator_ratio": 1.0,
        }
    )
    escalators_ts = pd.concat(
        [nrel118_escalators_ts, gens_non_escalated], ignore_index=True
    )

    # Merge
    gens = gens.merge(escalators_ts, on="gen_name", how="right")
    gens["max_p_mw"] *= gens["escalator_ratio"]
    gens["min_p_mw"] *= gens["escalator_ratio"]

    # Return results
    gens.sort_values(["datetime", "gen_name"], inplace=True, ignore_index=True)
    cols = ["datetime", "gen_name", "max_p_mw", "min_p_mw"]
    if path_transformed_data:
        gens[cols].to_csv(path_transformed_data, header=True, index=False)
    else:
        return gens[cols]


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 4:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython "
            "transform_gens_escalated_ts.py path_transformed_gens "
            "path_parsed_nrel118_escalators_ts path_transformed_data\n"
        )

    # Run
    transform_gens_escalated_ts(
        transformed_gens=sys.argv[1],
        parsed_nrel118_escalators_ts=sys.argv[2],
        path_transformed_data=sys.argv[3],
    )
