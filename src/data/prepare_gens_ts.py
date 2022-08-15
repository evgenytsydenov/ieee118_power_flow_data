import sys
from typing import Optional

import numpy as np
import pandas as pd

from definitions import DATE_FORMAT, DATE_RANGE, FILL_METHOD
from src.utils.data_loaders import load_df_data


def prepare_gens_ts(
    parsed_nrel118_winds_ts: str | pd.DataFrame,
    parsed_nrel118_solars_ts: str | pd.DataFrame,
    parsed_nrel118_hydros_ts: str | pd.DataFrame,
    parsed_nrel118_hydros_nondisp_ts: str | pd.DataFrame,
    transformed_gens_escalated_ts: str | pd.DataFrame,
    parsed_nrel118_outages_ts: str | pd.DataFrame,
    path_prepared_data: Optional[str] = None,
) -> Optional[pd.DataFrame]:
    """Prepare final generation time-series data.

    Args:
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
        parsed_nrel118_outages_ts: Path or dataframe with time-series outage data
          from the NREL-118 dataset.
        path_prepared_data: Path to save prepared data.

    Returns:
        Prepared data or None if `path_prepared_data` is passed and the data were saved.
    """

    # Load gens data
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
            dtypes={"datetime": str, "gen_name": str, "p__mw": float},
        )
        gen_ts.append(gen_data)
    gens = pd.concat(gen_ts, ignore_index=True)

    # Temporary assumptions
    gens["v_set__kv"] = np.nan
    gens["q_max__mvar"] = np.nan
    gens["q_min__mvar"] = np.nan

    # Set datetime as index, drop unused variables
    gens["datetime"] = pd.to_datetime(gens["datetime"], format=DATE_FORMAT)
    gens = gens.pivot(
        index="datetime",
        columns=["gen_name"],
        values=["p__mw", "q_min__mvar", "q_max__mvar", "v_set__kv"],
    )
    if FILL_METHOD == "pad":
        fill_method = "pad"
    else:
        raise AttributeError(f"Unknown value of FILL_METHOD: {FILL_METHOD}")
    gens.fillna(method=fill_method, inplace=True)
    gens.columns = [f"{col[1]}__{col[0]}" for col in gens.columns]

    # Extract necessary date range
    start_date, end_date, frequency = DATE_RANGE
    mask = (gens.index >= start_date) & (gens.index < end_date)
    gens = gens[mask].asfreq(frequency, method=fill_method)

    # Add info about outages
    outages_ts = load_df_data(
        data=parsed_nrel118_outages_ts,
        dtypes={"datetime": str, "gen_name": str, "in_outage": bool},
    )
    outages_ts["datetime"] = pd.to_datetime(outages_ts["datetime"], format=DATE_FORMAT)
    outages_ts["in_service"] = ~outages_ts["in_outage"]
    outages_ts = outages_ts.pivot(
        index="datetime",
        columns=["gen_name"],
        values=["in_service"],
    )
    outages_ts.fillna(method="pad", inplace=True)
    mask = (outages_ts.index >= start_date) & (outages_ts.index < end_date)
    outages_ts = outages_ts[mask].asfreq(frequency, method="pad")
    outages_ts.columns = [f"{col[0]}__in_service" for col in outages_ts.columns]

    # Return results
    gens = pd.concat([gens, outages_ts], axis=1)
    if path_prepared_data:
        gens.to_csv(
            path_prepared_data, header=True, index=True, date_format=DATE_FORMAT
        )
    else:
        return gens


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 8:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython prepare_gens_ts.py "
            "path_parsed_nrel118_wind_ts path_parsed_nrel118_solar_ts "
            "path_parsed_nrel118_hydro_ts path_parsed_nrel118_hydro_nondisp_ts "
            "path_transformed_gens_escalated_ts path_parsed_nrel118_outages_ts "
            "path_prepared_data\n"
        )

    # Run
    prepare_gens_ts(
        parsed_nrel118_winds_ts=sys.argv[1],
        parsed_nrel118_solars_ts=sys.argv[2],
        parsed_nrel118_hydros_ts=sys.argv[3],
        parsed_nrel118_hydros_nondisp_ts=sys.argv[4],
        transformed_gens_escalated_ts=sys.argv[5],
        parsed_nrel118_outages_ts=sys.argv[6],
        path_prepared_data=sys.argv[7],
    )
