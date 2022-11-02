import sys
from typing import Optional

import pandas as pd

from definitions import PLANT_MODE
from src.utils.data_loaders import load_df_data


def transform_gens(
    parsed_nrel118_gens: str | pd.DataFrame,
    prepared_buses: str | pd.DataFrame,
    path_transformed_data: Optional[str] = None,
) -> Optional[pd.DataFrame]:
    """Group generators by bus to represent as a power plant.

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
        },
    )
    buses = load_df_data(
        data=prepared_buses,
        dtypes={"bus_name": str, "is_slack": bool},
    )

    # Optimized gens
    gens_optimized = [
        "combined_cycle_gas_017",
        "combined_cycle_gas_020",
        "combined_cycle_gas_023",
        "combined_cycle_gas_024",
        "combined_cycle_gas_025",
        "combined_cycle_gas_026",
        "combined_cycle_gas_031",
        "combined_cycle_gas_034",
        "combined_cycle_gas_035",
        "combined_cycle_gas_036",
        "combustion_gas_011",
        "combustion_gas_012",
        "combustion_gas_015",
        "combustion_gas_016",
        "combustion_gas_020",
        "steam_gas_003",
        "steam_gas_006",
        "steam_gas_007",
        "steam_gas_008",
        "steam_gas_009",
    ]
    gens_missed = [
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
    gens_optimized += gens_missed
    gens[["is_optimized", "is_ts_missed"]] = False
    gens.loc[gens["gen_name"].isin(gens_optimized), "is_optimized"] = True
    gens.loc[gens["gen_name"].isin(gens_missed), "is_ts_missed"] = True

    # Add bus info
    gens = gens.merge(buses, on="bus_name", how="left")

    # Group generators by bus
    cols = [
        "bus_name",
        "gen_name",
        "max_p_mw",
        "min_p_mw",
        "is_slack",
        "is_optimized",
        "is_ts_missed",
    ]
    if PLANT_MODE:
        gens.sort_values("bus_name", inplace=True, ignore_index=True)
        gens["plant_name"] = "plant_" + gens["bus_name"].str.lstrip("bus_")
        cols.insert(0, "plant_name")

    # Return results
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
