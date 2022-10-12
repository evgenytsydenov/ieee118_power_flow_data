import warnings
from abc import ABC, abstractmethod
from datetime import datetime

from tqdm import tqdm

from definitions import DATE_FORMAT, MODEL_NAME_FORMAT
from src.utils.data_loaders import load_df_data


class BaseRegimeSampler(ABC):
    """Base class for creating power regimes."""

    def __init__(self) -> None:
        """Base class for creating power regimes."""
        self._buses = None
        self._branches = None
        self._loads = None
        self._loads_ts = None
        self._gens = None
        self._gens_ts = None
        self._model = None

    def load_data(
        self,
        path_buses: str,
        path_branches: str,
        path_loads: str,
        path_loads_ts: str,
        path_gens: str,
        path_gens_ts: str,
    ) -> None:
        """Load data for creating regimes.

        Args:
            path_buses: Path to bus info.
            path_branches: Path to branch info.
            path_loads: Path to load info.
            path_loads_ts: Path to load time-series info.
            path_gens: Path to data of generators or plants (if `plants_mode` is True).
            path_gens_ts: Path to time-series data of generators
                or plants (if `plants_mode` is True).
        """
        self._buses = load_df_data(
            path_buses,
            dtypes={
                "bus_name": str,
                "region": str,
                "in_service": bool,
                "v_rated_kv": float,
            },
        )
        self._branches = load_df_data(
            data=path_branches,
            dtypes={
                "branch_name": str,
                "from_bus": str,
                "to_bus": str,
                "parallel": str,
                "in_service": bool,
                "r_ohm": float,
                "x_ohm": float,
                "b_µs": float,
                "trafo_ratio_rel": float,
                "max_i_ka": float,
            },
        )
        self._loads = load_df_data(
            data=path_loads,
            dtypes={
                "bus_name": str,
                "load_name": str,
            },
        )
        self._loads_ts = load_df_data(
            data=path_loads_ts,
            dtypes={
                "datetime": str,
                "load_name": str,
                "in_service": bool,
                "q_mvar": float,
                "p_mw": float,
            },
        )
        self._loads_ts.sort_values(["datetime", "load_name"], inplace=True)
        self._loads_ts.set_index("datetime", inplace=True)

        self._gens = load_df_data(
            data=path_gens, dtypes={"bus_name": str, "gen_name": str}
        )
        self._gens_ts = load_df_data(
            data=path_gens_ts,
            dtypes={
                "datetime": str,
                "gen_name": str,
                "in_service": bool,
                "q_max_mvar": float,
                "q_min_mvar": float,
                "p_mw": float,
                "v_set_kv": float,
            },
        )
        self._gens_ts.sort_values(["datetime", "gen_name"], inplace=True)
        self._gens_ts.set_index("datetime", inplace=True)

    def start(self, path_models: str, display: bool = False) -> None:
        """Start sampling process.

        Args:
            path_models: Path to save models.
            display: If to show progress bar.
        """
        # Create base model
        self._build_model()

        # Timestamps are equal for all time-series data
        timestamps = self._gens_ts.index.unique()
        for timestamp in tqdm(timestamps, disable=not display):

            # Refresh regime data in accordance to datetime
            self._apply_next_timestamp(timestamp)

            # Calculate power flows
            is_converged = self._calculate_regime()
            if not is_converged:
                warnings.warn(f"Regime at {timestamp} did not converge.")

            # Save model
            model_name = datetime.strptime(timestamp, DATE_FORMAT).strftime(
                MODEL_NAME_FORMAT
            )
            self._save_model(path=path_models, model_name=model_name)
            break

    @abstractmethod
    def _build_model(self) -> None:
        """Create power flow model."""
        raise NotImplementedError

    @abstractmethod
    def _save_model(self, path: str, model_name: str) -> None:
        """Save model.

        Args:
            path: Path to save the model.
            model_name: Model name.
        """
        raise NotImplementedError

    @abstractmethod
    def _apply_next_timestamp(self, timestamp: str) -> None:
        """Refresh regime data in accordance to datetime.

        Args:
            timestamp: Current datetime.
        """
        raise NotImplementedError

    @abstractmethod
    def _calculate_regime(self) -> bool:
        """Calculate power flows.

        Returns:
            True if the calculation was successful, False otherwise.
        """
        raise NotImplementedError
