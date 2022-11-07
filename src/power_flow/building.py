import os
import sys

import pandas as pd

from definitions import F_HZ, POWER_FLOW_ENGINE, S_BASE_MVA


def building(
    buses: str | pd.DataFrame,
    branches: str | pd.DataFrame,
    loads: str | pd.DataFrame,
    loads_ts: str | pd.DataFrame,
    gens: str | pd.DataFrame,
    gens_ts: str | pd.DataFrame,
    path_samples: str,
) -> None:
    """Start building power flow cases.

    Args:
        buses: Path or DataFrame with bus data.
        branches: Path or DataFrame with branch data.
        loads: Path or DataFrame with load data.
        loads_ts: Path or DataFrame with load time-series data.
        gens: Path or DataFrame with generation data.
        gens_ts: Path or DataFrame with generation time-series data.
        path_samples: Path to save created power flow cases.
    """
    # Create builder
    match POWER_FLOW_ENGINE:
        case "pandapower":

            from src.power_flow.builders import PandaPowerFlowBuilder

            builder = PandaPowerFlowBuilder(f_hz=F_HZ, s_base_mva=S_BASE_MVA)
        case _:
            raise AttributeError(f"Unknown power flow engine: {POWER_FLOW_ENGINE}.")

    # Load data
    builder.load_data(
        buses=buses,
        branches=branches,
        loads=loads,
        loads_ts=loads_ts,
        gens=gens,
        gens_ts=gens_ts,
    )

    # Start building process
    os.makedirs(path_samples)
    builder.run(path_samples=path_samples, display=False)


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 8:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython "
            "building.py path_buses path_branches path_loads "
            "path_loads_ts path_gens path_gens_ts path_samples\n"
        )

    # Run
    building(
        buses=sys.argv[1],
        branches=sys.argv[2],
        loads=sys.argv[3],
        loads_ts=sys.argv[4],
        gens=sys.argv[5],
        gens_ts=sys.argv[6],
        path_samples=sys.argv[7],
    )
