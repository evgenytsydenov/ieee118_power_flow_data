import sys
from datetime import datetime
from typing import Optional

import pandas as pd

from definitions import DATE_FORMAT
from src.utils.data_loaders import load_df_data


def transform_gens_ts(
    parsed_nrel118_winds_ts: str | pd.DataFrame,
    parsed_nrel118_solars_ts: str | pd.DataFrame,
    parsed_nrel118_hydros_ts: str | pd.DataFrame,
    parsed_nrel118_hydros_nondisp_ts: str | pd.DataFrame,
    transformed_gens_escalated_ts: str | pd.DataFrame,
    transformed_gens: str | pd.DataFrame,
    path_transformed_data: Optional[str] = None,
) -> Optional[pd.DataFrame]:
    """Combine time-series data about generator outputs.

    Args:
        transformed_gens: Path or dataframe with generation data.
        parsed_nrel118_winds_ts: Path or dataframe with time-series wind data
          from the NREL-118 dataset.
        parsed_nrel118_solars_ts: Path or dataframe with time-series solar data
          from the NREL-118 dataset.
        parsed_nrel118_hydros_ts: Path or dataframe with time-series hydro data
          from the NREL-118 dataset.
        parsed_nrel118_hydros_nondisp_ts: Path or dataframe with time-series data
          of non-dispatchable hydro plants from the NREL-118 dataset.
        transformed_gens_escalated_ts: Path or dataframe with transformed time-series
          data of generator adjusted by escalators from the NREL-118 dataset.
        path_transformed_data: Path to save transformed data.

    Returns:
        Transformed data or None if `path_transformed_data` is passed
          and the data were saved.
    """
    # Load gens time-series data
    gen_ts = []
    for data in [
        parsed_nrel118_winds_ts,
        parsed_nrel118_solars_ts,
        parsed_nrel118_hydros_ts,
        parsed_nrel118_hydros_nondisp_ts,
        transformed_gens_escalated_ts,
    ]:
        gen_data = load_df_data(
            data=data,
            dtypes={"datetime": str, "gen_name": str, "p_mw": float},
        )
        gen_ts.append(gen_data)

    # Generators whose outputs were missed
    gens_missed_names = [
        "biomass_059",
        "biomass_060",
        "combined_cycle_gas_040",
        "combustion_gas_008",
        "combustion_gas_021",
        "combustion_gas_022",
        "combustion_gas_023",
        "combustion_gas_024",
        "combustion_gas_025",
        "combustion_gas_026",
        "combustion_gas_046",
        "combustion_gas_047",
        "combustion_gas_048",
        "combustion_gas_049",
        "combustion_gas_072",
        "combustion_gas_073",
        "hydro_001",
        "hydro_002",
        "hydro_003",
        "hydro_004",
        "hydro_005",
        "hydro_006",
        "hydro_007",
        "hydro_008",
        "hydro_009",
        "hydro_010",
        "hydro_011",
        "hydro_012",
        "hydro_013",
        "hydro_014",
        "hydro_015",
    ]
    gens_missed = pd.DataFrame(
        data={
            "gen_name": gens_missed_names,
            "datetime": datetime(2024, 1, 1, 0, 0, 0).strftime(DATE_FORMAT),
            "p_mw": 0,
        }
    )
    gen_ts.append(gens_missed)
    gen_ts = pd.concat(gen_ts, ignore_index=True)

    # Load gens data
    gens = load_df_data(
        data=transformed_gens,
        dtypes={"gen_name": str, "v_rated_kv": float, "max_p_mw": float},
    )

    # Join info about buses and gens
    gen_ts = gen_ts.merge(gens, on="gen_name", how="left")

    # Clip outputs which exceed the max limit
    gen_ts["p_mw"].clip(upper=gen_ts["max_p_mw"], inplace=True)

    # Assumptions
    gen_ts["q_max_mvar"] = 0.7 * gen_ts["max_p_mw"]
    gen_ts["q_min_mvar"] = -0.3 * gen_ts["max_p_mw"]
    gen_ts["v_set_kv"] = gen_ts["v_rated_kv"]

    # Return results
    gen_ts.sort_values(["datetime", "gen_name"], inplace=True, ignore_index=True)
    cols = ["datetime", "gen_name", "p_mw", "v_set_kv", "q_min_mvar", "q_max_mvar"]
    if path_transformed_data:
        gen_ts[cols].to_csv(path_transformed_data, header=True, index=False)
    else:
        return gen_ts[cols]


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 8:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython "
            "transform_gens_ts.py path_parsed_nrel118_winds_ts "
            "path_parsed_nrel118_solars_ts path_parsed_nrel118_hydros_ts "
            "path_parsed_nrel118_hydros_nondisp_ts path_transformed_gens_escalated_ts "
            "path_transformed_gens path_transformed_data\n"
        )

    # Run
    transform_gens_ts(
        parsed_nrel118_winds_ts=sys.argv[1],
        parsed_nrel118_solars_ts=sys.argv[2],
        parsed_nrel118_hydros_ts=sys.argv[3],
        parsed_nrel118_hydros_nondisp_ts=sys.argv[4],
        transformed_gens_escalated_ts=sys.argv[5],
        transformed_gens=sys.argv[6],
        path_transformed_data=sys.argv[7],
    )
