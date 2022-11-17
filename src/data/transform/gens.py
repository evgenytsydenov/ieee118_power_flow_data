import sys
from typing import Optional

import pandas as pd

from src.utils.data_loaders import load_df_data


def transform_gens(
    parsed_nrel118_gens: str | pd.DataFrame,
    prepared_buses: str | pd.DataFrame,
    path_transformed_data: Optional[str] = None,
) -> Optional[pd.DataFrame]:
    """Transform gen data.

    Args:
        path_transformed_data: Path to save transformed data.
        prepared_buses: Path or dataframe with bus data.
        parsed_nrel118_gens: Path or dataframe with parsed generation data.

    Returns:
        Transformed data or None if `path_transformed_data` is passed
          and the data were saved.
    """
    # Load data
    gens = load_df_data(
        data=parsed_nrel118_gens,
        dtypes={
            "gen_name": str,
            "bus_name": str,
            "max_p_mw": float,
            "min_p_mw": float,
            "opt_category": str,
        },
    )
    buses = load_df_data(
        data=prepared_buses,
        dtypes={"bus_name": str, "is_slack": bool},
    )

    # Specify which gens are optimized
    non_optimized = ["solar", "wind", "hydro"]
    gens.loc[gens["opt_category"].isin(non_optimized), "opt_category"] = "non_optimized"
    optimized_hydros = [f"hydro_{i:03}" for i in range(1, 16)]
    gens.loc[gens["gen_name"].isin(optimized_hydros), "opt_category"] = "real_time"

    # Add slack bus info
    gens = gens.merge(buses, on="bus_name", how="left")

    # Return results
    cols = [
        "gen_name",
        "bus_name",
        "max_p_mw",
        "min_p_mw",
        "is_slack",
        "opt_category",
    ]
    if path_transformed_data:
        gens[cols].to_csv(path_transformed_data, header=True, index=False)
    else:
        return gens[cols]


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 4:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython "
            "transform_gens.py path_parsed_nrel118_gens path_prepared_buses "
            "path_transformed_data\n"
        )

    # Run
    transform_gens(
        parsed_nrel118_gens=sys.argv[1],
        prepared_buses=sys.argv[2],
        path_transformed_data=sys.argv[3],
    )
