import os
import sys

from definitions import F_HZ, REGIME_SAMPLER, S_BASE_MVA
from src.model.samplers.pandapower import PandaRegimeSampler


def sampling(
    path_buses: str,
    path_branches: str,
    path_loads: str,
    path_loads_ts: str,
    path_gens: str,
    path_gens_ts: str,
    path_models: str,
) -> None:
    """Start sampling of power flow cases.

    Args:
        path_buses: Path or DataFrame with bus data.
        path_branches: Path or DataFrame with branch data.
        path_loads: Path or DataFrame with load data.
        path_loads_ts: Path or DataFrame with load time-series data.
        path_gens: Path or DataFrame with generation data.
        path_gens_ts: Path or DataFrame with generation time-series data.
        path_models: Path to save created models.
    """
    # Create sampler
    match REGIME_SAMPLER:
        case "pandapower":
            sampler = PandaRegimeSampler(f_hz=F_HZ, s_base_mva=S_BASE_MVA)
        case _:
            raise AttributeError(f"Unknown regime sampler: {REGIME_SAMPLER}.")

    # Load data
    sampler.load_data(
        path_buses=path_buses,
        path_branches=path_branches,
        path_loads=path_loads,
        path_loads_ts=path_loads_ts,
        path_gens=path_gens,
        path_gens_ts=path_gens_ts,
    )

    # Start sampling
    os.makedirs(path_models)
    sampler.start(path_models=path_models)


if __name__ == "__main__":
    # Check params
    if len(sys.argv) != 8:
        raise ValueError(
            "Incorrect arguments. Usage:\n\tpython "
            "sampling.py path_buses path_branches path_loads "
            "path_loads_ts path_gens path_gens_ts path_models\n"
        )

    # Run
    sampling(
        path_buses=sys.argv[1],
        path_branches=sys.argv[2],
        path_loads=sys.argv[3],
        path_loads_ts=sys.argv[4],
        path_gens=sys.argv[5],
        path_gens_ts=sys.argv[6],
        path_models=sys.argv[7],
    )
