import sys
from datetime import datetime
from typing import Optional

import pandas as pd

from definitions import DATE_FORMAT
from src.utils.data_loaders import load_df_data


def transform_outages_ts(
    parsed_nrel118_outages_ts: str | pd.DataFrame,
    path_transformed_data: Optional[str] = None,
) -> Optional[pd.DataFrame]:
    """Transform time-series data about generator outages.

    Args:
        parsed_nrel118_outages_ts: Path or dataframe with outage time-series data
         from the NREL-118 dataset.
        path_transformed_data: Path to save transformed data.

    Returns:
        Transformed data or None if `path_transformed_data` is passed
          and the data were saved.
    """
    # Load data
    outages = load_df_data(
        data=parsed_nrel118_outages_ts,
        dtypes={"datetime": str, "gen_name": str, "in_outage": bool},
    )
    outages["datetime"] = pd.to_datetime(outages["datetime"], format=DATE_FORMAT)

    # Convert "in_outage" into "in_service" parameter
    outages["in_service"] = ~outages["in_outage"]

    # In the dataframe, there are some unknown power plants, drop them
    to_drop = ["PSH_1", "PSH_2", "solar_76"]
    unknown_power_plants = outages[outages["gen_name"].isin(to_drop)].index
    outages.drop(unknown_power_plants, inplace=True)

    # Fix incorrect gen names
    to_fix = [
        ("2024-01-19 16:00:00", "internal_combustion_gas_2"),
        ("2024-01-21 05:00:00", "internal_combustion_gas_3"),
        ("2024-01-22 14:00:00", "internal_combustion_gas_4"),
        ("2024-01-24 03:00:00", "internal_combustion_gas_5"),
        ("2024-02-21 19:00:00", "internal_combustion_gas_6"),
        ("2024-02-23 08:00:00", "internal_combustion_gas_7"),
        ("2024-04-23 09:00:00", "internal_combustion_gas_8"),
        ("2024-04-24 22:00:00", "internal_combustion_gas_9"),
        ("2024-05-17 16:00:00", "internal_combustion_gas_10"),
        ("2024-05-19 05:00:00", "internal_combustion_gas_11"),
        ("2024-08-04 15:00:00", "internal_combustion_gas_12"),
        ("2024-08-06 04:00:00", "internal_combustion_gas_13"),
        ("2024-09-13 12:00:00", "internal_combustion_gas_14"),
        ("2024-09-15 01:00:00", "internal_combustion_gas_15"),
        ("2024-10-16 17:00:00", "internal_combustion_gas_16"),
        ("2024-10-18 06:00:00", "internal_combustion_gas_17"),
        ("2024-10-31 21:00:00", "internal_combustion_gas_18"),
        ("2024-11-02 10:00:00", "internal_combustion_gas_19"),
        ("2024-11-23 13:00:00", "internal_combustion_gas_20"),
        ("2024-11-25 02:00:00", "internal_combustion_gas_21"),
        ("2024-12-12 22:00:00", "internal_combustion_gas_22"),
        ("2024-12-14 11:00:00", "internal_combustion_gas_23"),
    ]
    for date, gen_name in to_fix:
        mask = (outages["datetime"] == datetime.strptime(date, "%Y-%m-%d %H:%M:%S")) & (
            outages["gen_name"] == gen_name
        )
        outages.loc[mask, "gen_name"] = "internal_combustion_gas_1"

    # Since there is no information about outages of the following gens,
    # it is assumed that they are always in service
    missing_gens = [
        "hydro_31",
        "biomass_53",
        "biomass_54",
        "biomass_55",
        "combined_cycle_gas_40",
        "combustion_gas_9",
        "combustion_gas_10",
        "combustion_gas_11",
        "combustion_gas_12",
        "combustion_gas_30",
        "combustion_gas_70",
        "steam_gas_1",
        "steam_gas_2",
        "steam_gas_3",
        "steam_gas_6",
        "steam_gas_7",
        "steam_gas_8",
        "steam_gas_9",
        "steam_gas_10",
    ]
    to_add = pd.DataFrame(
        data={
            "gen_name": missing_gens,
            "datetime": datetime(2024, 1, 1, 0, 0, 0),
            "in_service": True,
        }
    )

    # Concat old and new values
    outages = pd.concat([outages, to_add], ignore_index=True)
    outages.sort_values(by=["gen_name", "datetime"], inplace=True)

    # Return results
    cols = ["datetime", "gen_name", "in_service"]
    if path_transformed_data:
        outages[cols].to_csv(
            path_transformed_data, header=True, index=False, date_format=DATE_FORMAT
        )
    else:
        return outages[cols]


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 3:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython "
            "transform_outages_ts.py parsed_nrel118_outages_ts path_transformed_data\n"
        )

    # Run
    transform_outages_ts(
        parsed_nrel118_outages_ts=sys.argv[1],
        path_transformed_data=sys.argv[2],
    )
