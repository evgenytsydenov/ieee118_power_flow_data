import os
from abc import ABC, abstractmethod
from datetime import datetime
from multiprocessing import Manager, Pool, Queue, current_process
from threading import Thread
from typing import Any, Optional

import numpy as np
import pandas as pd
from tqdm import tqdm

from definitions import DATE_FORMAT, PLANT_MODE, SAMPLE_NAME_FORMAT
from src.utils.app_logger import get_logger, get_queue_logger, queue_listener
from src.utils.data_loaders import load_df_data


class BasePowerFlowBuilder(ABC):
    """Base class for building power flow cases."""

    def __init__(self) -> None:
        """Base class for building power flow cases."""
        self.timestamps = None
        self._logger = get_logger(__name__)
        self._is_plant_mode = PLANT_MODE
        self._buses = None
        self._branches = None
        self._loads = None
        self._loads_ts = None
        self._gens = None
        self._gens_ts = None

    def load_data(
        self,
        buses: str | pd.DataFrame,
        branches: str | pd.DataFrame,
        loads: str | pd.DataFrame,
        loads_ts: str | pd.DataFrame,
        gens: str | pd.DataFrame,
        gens_ts: str | pd.DataFrame,
    ) -> None:
        """Load data for building power flow cases.

        Args:
            buses: Path or DataFrame with bus data.
            branches: Path or DataFrame with branch data.
            loads: Path or DataFrame with load data.
            loads_ts: Path or DataFrame with load time-series data.
            gens: Path or DataFrame with generation data.
            gens_ts: Path or DataFrame with generation time-series data.
        """
        # Load raw data
        self._buses = load_df_data(
            buses,
            dtypes={
                "bus_name": str,
                "region": str,
                "in_service": bool,
                "v_rated_kv": float,
                "is_slack": bool,
                "min_v_pu": float,
                "max_v_pu": float,
                "x_coordinate": float,
                "y_coordinate": float,
            },
        )
        self._branches = load_df_data(
            data=branches,
            dtypes={
                "branch_name": str,
                "from_bus": str,
                "to_bus": str,
                "parallel": int,
                "in_service": bool,
                "r_ohm": float,
                "x_ohm": float,
                "b_µs": float,
                "trafo_ratio_rel": float,
                "max_i_ka": float,
            },
        )
        self._loads = load_df_data(
            data=loads,
            dtypes={
                "load_name": str,
                "bus_name": str,
            },
        )
        self._loads_ts = load_df_data(
            data=loads_ts,
            dtypes={
                "datetime": str,
                "load_name": str,
                "in_service": bool,
                "q_mvar": float,
                "p_mw": float,
            },
        )
        self._gens = load_df_data(
            data=gens,
            dtypes={
                "gen_name": str,
                "bus_name": str,
                "max_p_mw": float,
                "min_p_mw": float,
                "is_optimized": bool,
            },
        )
        self._gens_ts = load_df_data(
            data=gens_ts,
            dtypes={
                "datetime": str,
                "gen_name": str,
                "in_service": bool,
                "p_mw": float,
                "max_q_mvar": float,
                "min_q_mvar": float,
            },
        )

        # Assume datetime ranges in load and gen time-series are equal
        self.timestamps = sorted(self._gens_ts["datetime"].unique())

    def run(
        self,
        timestamp: Optional[str | list[str]] = None,
        path_sample: Optional[str] = None,
        display: bool = False,
        workers: int = 1,
    ) -> Optional[Any]:
        """Run the building process.

        Args:
            timestamp: Timestamps of power flow cases to calculate.
            path_sample: Path if it is necessary to save power flow cases.
            display: If to show a progress bar.
            workers: Number of workers to use.

        Returns:
            Power flow cases corresponding to the timestamp of the provided data.
        """
        # If one timestamp or one worker
        timestamps = self.timestamps if timestamp is None else timestamp
        timestamps = [timestamps] if isinstance(timestamps, str) else timestamps
        if len(timestamps) > 1 and (path_sample is None):
            self._logger.warning(
                "Samples will not be saved because `path_sample` is `None`."
            )
        workers_count = workers if workers > 0 else os.cpu_count()
        workers_count = min([workers_count, len(timestamps), os.cpu_count()])
        if workers != workers_count:
            self._logger.warning(
                f"The number of workers was changed to {workers_count}."
            )
        self._prepare_data()
        if workers_count == 1:
            return self._run(
                timestamps=timestamps, display=display, path_samples=path_sample
            )

        # Thread to capture logs
        manager = Manager()
        log_queue = manager.Queue(-1)
        log_thread = Thread(target=queue_listener, args=(__name__, log_queue))
        log_thread.start()

        # Start processes
        # Show progress bar only for the last worker
        args = []
        for worker_id, time_samples in enumerate(
            np.array_split(timestamps, workers_count)
        ):
            to_display = display * (worker_id + 1 == workers_count)
            args.append((time_samples.tolist(), path_sample, to_display, log_queue))
        with Pool(workers_count) as pool:
            pool.starmap(self._run, args)

        # Finish logging thread
        log_queue.put_nowait(None)
        log_thread.join()

    def _run(
        self,
        timestamps: list[str],
        path_samples: Optional[str] = None,
        display: bool = False,
        queue: Optional[Queue] = None,
    ) -> Optional[Any]:
        """Run the building process.

        Args:
            timestamps: Timestamps of power flow cases to calculate.
            path_samples: Path if it is necessary to save power flow cases.
            display: If to show a progress bar.
            queue: Queue for logs.
        Returns:
            Power flow cases corresponding to the timestamp of the provided data.
        """
        # Create base model
        model = self._build_base_model()

        # Prepare logger
        if queue is None:
            logger = self._logger
        else:
            proc_name = current_process().name.lower()
            logger_name = f"{__name__}.{proc_name}"
            logger = get_queue_logger(logger_name, queue)

        # Timestamps are equal for all time-series data
        to_return = (len(timestamps) == 1) and (path_samples is None)
        for time_sample in tqdm(timestamps, disable=not display):

            # Refresh sample data in accordance to the current datetime
            self._apply_next_timestamp(model, time_sample)

            # Calculate power flows
            is_opf_converged = self._calculate_opf(model)
            if is_opf_converged:
                is_pf_converged = self._calculate_power_flow(model)
                if not is_pf_converged:
                    logger.info(
                        f"Power flow estimation at {time_sample}" f" did not converge."
                    )
            else:
                logger.info(f"OPF estimation at {time_sample} did not converge.")

            # Save created case
            if path_samples:
                sample_name = datetime.strptime(time_sample, DATE_FORMAT).strftime(
                    SAMPLE_NAME_FORMAT
                )
                self._save_sample(model, path=path_samples, sample_name=sample_name)
        return model if to_return else None

    @abstractmethod
    def _build_base_model(self) -> Any:
        """Create power flow model.

        Returns:
            Model with predefined parameters.
        """
        raise NotImplementedError

    @abstractmethod
    def _save_sample(self, model: Any, path: str, sample_name: str) -> None:
        """Save sample.

        Args:
            model: Power system model.
            path: Path to save the sample.
            sample_name: Sample name.
        """
        raise NotImplementedError

    @abstractmethod
    def _apply_next_timestamp(self, model: Any, timestamp: str) -> None:
        """Refresh data in accordance to the timestamp.

        Args:
            model: Power system model.
            timestamp: Current datetime.
        """
        raise NotImplementedError

    @abstractmethod
    def _calculate_power_flow(self, model: Any) -> bool:
        """Calculate power flows.

        Args:
            model: Power system model.
        Returns:
            True if the calculation was successful, False otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def _calculate_opf(self, model: Any) -> bool:
        """Solve optimal power flow task.

        Args:
            model: Power system model.
        Returns:
            True if the calculation was successful, False otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def _prepare_data(self) -> None:
        """Prepare initial data for faster access."""
        raise NotImplementedError
