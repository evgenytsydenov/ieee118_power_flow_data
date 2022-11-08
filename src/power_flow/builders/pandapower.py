import logging
import math
import os
import warnings
from typing import Any

import numpy as np
import pandapower as pp
import pandas as pd
from pandapower import LoadflowNotConverged, OPFNotConverged

from src.power_flow.builders.base import BasePowerFlowBuilder

# Supress warnings
warnings.simplefilter(action="ignore", category=FutureWarning)
logging.getLogger("pandapower.opf.make_objective").setLevel(logging.ERROR)


class PandaPowerFlowBuilder(BasePowerFlowBuilder):
    """Class for creating power flow cases using PandaPower.

    Args:
        s_base_mva: Base power.
        f_hz: Power system frequency.
    """

    def __init__(self, s_base_mva: float, f_hz: float) -> None:
        super().__init__()
        self.s_base_mva = s_base_mva
        self.f_hz = f_hz
        self._bus_name_to_id = None
        self._bus_name_to_v_rate = None
        self._slack_bus_id = None
        self._gens_prep = None
        self._gens_ts_prep = None
        self._load_cols = ["in_service", "p_mw", "q_mvar"]
        self._gen_cols = [
            "in_service",
            "p_mw",
            "min_q_mvar",
            "max_q_mvar",
            "max_p_mw",
            "min_p_mw",
        ]

    @property
    def sample(self) -> Any:
        """Current power flow sample."""
        if self._model is None:
            raise ValueError("The model should be built first.")
        return self._model.deepcopy()

    def _prepare_data(self) -> None:
        """Prepare data for OPF and group gens in plants if needed."""

        # Add plant names
        gens = self._gens.copy()
        if self._is_plant_mode:
            gens.sort_values("bus_name", inplace=True, ignore_index=True)
            bus_index = gens["bus_name"].str.lstrip("bus_")
            gens["plant_name"] = "plant_" + bus_index

        # Limits for OPF
        gen_ts = pd.merge(self._gens_ts, gens, on="gen_name", how="left", copy=True)
        gen_ts["max_p_opf_mw"] = np.where(
            gen_ts["is_optimized"], gen_ts["max_p_mw"], gen_ts["p_mw"]
        )
        gen_ts["min_p_opf_mw"] = np.where(
            gen_ts["is_optimized"], gen_ts["min_p_mw"], gen_ts["p_mw"]
        )
        cols = ["p_mw", "max_q_mvar", "min_q_mvar", "max_p_opf_mw", "min_p_opf_mw"]
        gen_ts.loc[~gen_ts["in_service"], cols] = np.nan

        # Group gen parameters
        if self._is_plant_mode:
            agg_funcs = {
                "p_mw": "sum",
                "max_q_mvar": "sum",
                "min_q_mvar": "sum",
                "max_p_opf_mw": "sum",
                "min_p_opf_mw": "sum",
                "in_service": "sum",
            }
            gen_ts = gen_ts.groupby(["plant_name", "datetime"], as_index=False).agg(
                agg_funcs
            )

            # If the number of gens, which are in service, equals to zero,
            # the plant is out of service and its parameters should be undefined
            gen_ts["in_service"] = gen_ts["in_service"].astype(bool)
            gen_ts.loc[~gen_ts["in_service"], cols] = np.nan

            # Modify gen info
            gens.drop(columns=["gen_name"], inplace=True)
            funcs = {"max_p_mw": "sum", "min_p_mw": "min"}
            gens = gens.groupby(["bus_name", "plant_name"], as_index=False).agg(funcs)

            # Rename columns for consistency in further scripts
            gen_ts.rename(columns={"plant_name": "gen_name"}, inplace=True)
            gens.rename(columns={"plant_name": "gen_name"}, inplace=True)

        # Prepare gen data for faster access
        self._gens_prep = gens.sort_values("gen_name")
        self._gens_ts_prep = (
            gen_ts[["datetime", "gen_name", "in_service", *cols]]
            .rename(columns={"max_p_opf_mw": "max_p_mw", "min_p_opf_mw": "min_p_mw"})
            .astype({col: float for col in self._gen_cols})
            .sort_values(["datetime", "gen_name"])
            .set_index("datetime")
        )

        # Prepare load data for faster access
        self._loads.sort_values("load_name", inplace=True)
        self._loads_ts[self._load_cols] = self._loads_ts[self._load_cols].astype(float)
        self._loads_ts.sort_values(["datetime", "load_name"], inplace=True)
        if "datetime" not in self._loads_ts.index.names:
            self._loads_ts.set_index("datetime", inplace=True)

    def _build_base_model(self) -> None:
        """Create power flow model."""
        # Some initial preparations
        self._prepare_data()

        # Create empty network
        self._model = pp.create_empty_network(
            sn_mva=self.s_base_mva, f_hz=self.f_hz, add_stdtypes=False
        )

        # Prepare and add buses first
        self._add_buses()

        # For faster access
        self._bus_name_to_id = pd.Series(
            data=self._model.bus.index.values, index=self._model.bus["name"].values
        )
        self._bus_name_to_v_rate = pd.Series(
            data=self._model.bus["vn_kv"].values, index=self._model.bus["name"].values
        )

        # Prepare and add the rest
        self._add_lines()
        self._add_transformers()
        self._add_loads()
        self._add_generators()
        self._add_slack()

    def _add_slack(self) -> None:
        """Add slack bus info to the power flow model."""
        slack_bus = self._buses.loc[self._buses["is_slack"], "bus_name"].values[0]
        self._slack_bus_id = self._bus_name_to_id[slack_bus]
        pp.create_ext_grid(
            self._model,
            bus=self._slack_bus_id,
            name=slack_bus,
            vm_pu=1,
            va_degree=0,
            in_service=True,
            controllable=True,
        )

    def _add_buses(self) -> None:
        """Add bus info to the power flow model."""

        # Prepare
        self._buses.sort_values("bus_name", inplace=True)

        # Add buses
        pp.create_buses(
            self._model,
            nr_buses=len(self._buses),
            vn_kv=self._buses["v_rated_kv"],
            name=self._buses["bus_name"],
            zone=self._buses["region"],
            in_service=self._buses["in_service"],
            max_vm_pu=self._buses["max_v_pu"],
            min_vm_pu=self._buses["min_v_pu"],
            geodata=list(zip(self._buses["x_coordinate"], self._buses["y_coordinate"])),
        )

    def _add_lines(self) -> None:
        """Add line info to the power flow model."""

        # Get only lines
        lines = self._branches[self._branches["trafo_ratio_rel"].isna()]
        lines.sort_values("branch_name", inplace=True)

        # Convert bus names to indices
        lines["from_bus_id"] = lines["from_bus"].map(self._bus_name_to_id)
        lines["to_bus_id"] = lines["to_bus"].map(self._bus_name_to_id)

        # Convert to farads
        lines["c_nf"] = lines["b_µs"] * 1e3 / (2 * self.f_hz * math.pi)

        # Add lines to the model
        pp.create_lines_from_parameters(
            self._model,
            name=lines["branch_name"],
            from_buses=lines["from_bus_id"],
            to_buses=lines["to_bus_id"],
            parallel=lines["parallel"],
            r_ohm_per_km=lines["r_ohm"],
            x_ohm_per_km=lines["x_ohm"],
            c_nf_per_km=lines["c_nf"],
            max_i_ka=lines["max_i_ka"],
            in_service=lines["in_service"],
            length_km=1,
            max_loading_percent=100,
            type="ol",
        )

    def _add_transformers(self) -> None:
        """Add transformer info to the power flow model."""

        # Get only transformers
        trafos = self._branches[~self._branches["trafo_ratio_rel"].isna()]
        trafos.sort_values("branch_name", inplace=True)

        # Convert bus names to indices
        trafos["from_bus_id"] = trafos["from_bus"].map(self._bus_name_to_id)
        trafos["to_bus_id"] = trafos["to_bus"].map(self._bus_name_to_id)

        # Consider from_bus is a high voltage level bus
        vn_hv_kv = self._bus_name_to_v_rate.loc[trafos["from_bus"]].values
        vn_lv_kv = self._bus_name_to_v_rate.loc[trafos["to_bus"]].values

        # Calculate trafo parameters
        z_base_net = vn_hv_kv**2 / self.s_base_mva
        s_base_trafo_mva = trafos["max_i_ka"] * vn_hv_kv * 3**0.5
        vk_percent = (
            100 * (trafos["x_ohm"] / z_base_net) * (s_base_trafo_mva / self.s_base_mva)
        )
        vkr_percent = (
            100 * (trafos["r_ohm"] / z_base_net) * (s_base_trafo_mva / self.s_base_mva)
        )
        tap_diff = (trafos["trafo_ratio_rel"] - 1).values
        tap_step_percent = np.abs(tap_diff) * 100
        tap_pos = np.sign(tap_diff)

        # Add trafos to the model
        pp.create_transformers_from_parameters(
            self._model,
            name=trafos["branch_name"],
            hv_buses=trafos["from_bus_id"],
            lv_buses=trafos["to_bus_id"],
            sn_mva=s_base_trafo_mva,
            vn_hv_kv=vn_hv_kv,
            vn_lv_kv=vn_lv_kv,
            vk_percent=vk_percent,
            vkr_percent=vkr_percent,
            parallel=trafos["parallel"],
            in_service=trafos["in_service"],
            tap_pos=tap_pos,
            tap_step_percent=tap_step_percent,
            tap_side="hv",
            tap_neutral=0,
            pfe_kw=0,
            i0_percent=0,
            max_loading_percent=100,
        )

    def _add_loads(self) -> None:
        """Add load info to the power flow model."""

        # Prepare load info
        self._loads["bus_id"] = self._loads["bus_name"].map(self._bus_name_to_id)

        # Add basic info
        # Actual parameters will be populated later for each timestamp
        pp.create_loads(
            self._model,
            name=self._loads["load_name"],
            buses=self._loads["bus_id"],
            p_mw=0,
            q_mvar=0,
            in_service=True,
            controllable=False,
        )

    def _add_generators(self) -> None:
        """Add gen info to the power flow model."""

        # Prepare gen info
        self._gens_prep["bus_id"] = self._gens_prep["bus_name"].map(
            self._bus_name_to_id
        )

        # Add basic info
        # Actual parameters will be populated later for each timestamp
        pp.create_gens(
            self._model,
            name=self._gens_prep["gen_name"],
            buses=self._gens_prep["bus_id"],
            p_mw=0,
            max_q_mvar=0,
            min_q_mvar=0,
            min_p_mw=0,
            max_p_mw=0,
            vm_pu=1,
            in_service=True,
            controllable=True,
        )

    def _apply_next_timestamp(self, timestamp: str) -> None:
        """Refresh data in accordance to the timestamp.

        Prepare the model for OPF.

        Args:
            timestamp: Current datetime.
        """
        # Set load
        # Assume that load_ts is sorted by datetime and load_name
        self._model.load[self._load_cols] = self._loads_ts.loc[
            timestamp, self._load_cols
        ].values

        # Set gens
        # Assume that gen_ts_prep is sorted by datetime and gen_name
        self._model.gen[self._gen_cols] = self._gens_ts_prep.loc[
            timestamp, self._gen_cols
        ].values
        self._model.gen["controllable"] = True

    def _save_sample(self, path: str, sample_name: str) -> None:
        """Save sample.

        Args:
            path: Path to save the sample.
            sample_name: Sample name.
        """
        sample_path = os.path.join(path, f"{sample_name}.json")
        pp.to_json(self._model, sample_path)

    def _calculate_opf(self) -> bool:
        """Solve optimal power flow task.

        Returns:
            True if the calculation was successful, False otherwise.
        """
        try:
            # Run OPF
            pp.runopp(self._model, init="flat")

            # Add optimized values to the model
            self._model.gen[["p_mw", "vm_pu"]] = self._model.res_gen[
                ["p_mw", "vm_pu"]
            ].values
            self._model.ext_grid["vm_pu"] = self._model.res_bus.loc[
                self._slack_bus_id, "vm_pu"
            ]
        except OPFNotConverged:
            pp.clear_result_tables(self._model)
            return False

        finally:

            # Restore original limits of gen outputs and controllable flag
            self._model.gen[["min_p_mw", "max_p_mw"]] = self._gens_prep[
                ["min_p_mw", "max_p_mw"]
            ].values
            self._model.gen["controllable"] = self._gens_prep["is_optimized"].values

        return True

    def _calculate_power_flow(self) -> bool:
        """Calculate power flows.

        Returns:
            True if the calculation was successful, False otherwise.
        """
        try:
            pp.runpp(
                self._model,
                algorithm="nr",
                calculate_voltage_angles=True,
                init="flat",
                enforce_q_lims=True,
            )
        except LoadflowNotConverged:
            pp.clear_result_tables(self._model)
            return False
        return True
