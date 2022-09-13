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
    prepared_buses: str | pd.DataFrame,
    prepared_gens: str | pd.DataFrame,
    path_transformed_data: Optional[str] = None,
) -> Optional[pd.DataFrame]:
    """Combine time-series data about generator outputs.

    Args:
        prepared_gens: Path or dataframe with generation data.
        prepared_buses: Path or dataframe with bus data.
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
    gens_optimized_names = [
        "biomass_59",
        "biomass_60",
        "combined_cycle_gas_40",
        "combustion_gas_8",
        "combustion_gas_21",
        "combustion_gas_22",
        "combustion_gas_23",
        "combustion_gas_24",
        "combustion_gas_25",
        "combustion_gas_26",
        "combustion_gas_46",
        "combustion_gas_47",
        "combustion_gas_48",
        "combustion_gas_49",
        "combustion_gas_72",
        "combustion_gas_73",
        "hydro_1",
        "hydro_2",
        "hydro_3",
        "hydro_4",
        "hydro_5",
        "hydro_6",
        "hydro_7",
        "hydro_8",
        "hydro_9",
        "hydro_10",
        "hydro_11",
        "hydro_12",
        "hydro_13",
        "hydro_14",
        "hydro_15",
    ]
    gens_optimized = pd.DataFrame(
        data={
            "gen_name": gens_optimized_names,
            "datetime": datetime(2024, 1, 1, 0, 0, 0),
            "p_mw": 0,
        }
    )
    gen_ts.append(gens_optimized)
    gen_ts = pd.concat(gen_ts, ignore_index=True)

    # Load bus data
    buses = load_df_data(
        data=prepared_buses,
        dtypes={"bus_name": str, "v_rated_kv": float},
    )

    # Load gens data
    gens = load_df_data(
        data=prepared_gens,
        dtypes={"gen_name": str, "bus_name": str},
    )

    # Join info about buses and gens
    gens = gens.merge(buses, on="bus_name", how="left")
    gen_ts = gen_ts.merge(gens[["gen_name", "v_rated_kv"]], on="gen_name", how="left")

    # Assumptions
    gen_ts["q_max_mvar"] = 0.75 * gen_ts["p_mw"]
    gen_ts["q_min_mvar"] = -0.3 * gen_ts["p_mw"]
    gen_ts["v_set_kv"] = gen_ts["v_rated_kv"]

    # Return results
    cols = ["datetime", "gen_name", "p_mw", "v_set_kv", "q_min_mvar", "q_max_mvar"]
    if path_transformed_data:
        gen_ts[cols].to_csv(
            path_transformed_data, header=True, index=False, date_format=DATE_FORMAT
        )
    else:
        return gen_ts[cols]


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 9:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython "
            "transform_gens_ts.py parsed_nrel118_winds_ts parsed_nrel118_solars_ts "
            "parsed_nrel118_hydros_ts parsed_nrel118_hydros_nondisp_ts "
            "transformed_gens_escalated_ts prepared_buses prepared_gens "
            "path_transformed_data\n"
        )

    # Run
    transform_gens_ts(
        parsed_nrel118_winds_ts=sys.argv[1],
        parsed_nrel118_solars_ts=sys.argv[2],
        parsed_nrel118_hydros_ts=sys.argv[3],
        parsed_nrel118_hydros_nondisp_ts=sys.argv[4],
        transformed_gens_escalated_ts=sys.argv[5],
        prepared_buses=sys.argv[6],
        prepared_gens=sys.argv[7],
        path_transformed_data=sys.argv[8],
    )
