"""
data_source.py — DataSource Interface Layer

KEY ARCHITECTURAL DECISION: The simulation engine NEVER directly generates data.
It always asks a DataSource object. Swapping from simulated to real IoT data
later requires changing only ONE line.
"""

import random
import math
import os
import csv
import time
from abc import ABC, abstractmethod
from typing import Optional

import numpy as np


# ═══════════════════════════════════════════════════════════════════════
# ABSTRACT BASE CLASS
# ═══════════════════════════════════════════════════════════════════════

class DataSource(ABC):
    """Abstract base class for all data sources.

    The simulation engine calls these methods instead of generating
    data directly. This allows seamless swapping between synthetic,
    MQTT, CSV, and OPC-UA sources.
    """

    @abstractmethod
    def get_cycle_time(self, station_id: int) -> float:
        """Get the cycle time for a station in seconds.

        Args:
            station_id: The station identifier.

        Returns:
            Cycle time in seconds (positive float).
        """
        ...

    @abstractmethod
    def get_station_status(self, station_id: int) -> str:
        """Get the current status of a station.

        Args:
            station_id: The station identifier.

        Returns:
            One of: 'running', 'idle', 'broken'
        """
        ...

    @abstractmethod
    def get_breakdown_probability(self, station_id: int, utilization: float) -> float:
        """Get the probability of breakdown for a station.

        Args:
            station_id: The station identifier.
            utilization: Current machine utilization (0.0 to 1.0).

        Returns:
            Probability of breakdown (0.0 to 1.0).
        """
        ...


# ═══════════════════════════════════════════════════════════════════════
# VARIABILITY FACTORS BY CONDITION
# ═══════════════════════════════════════════════════════════════════════

VARIABILITY_FACTORS = {
    "good": 0.08,
    "average": 0.15,
    "poor": 0.25,
}


# ═══════════════════════════════════════════════════════════════════════
# IMPLEMENTATION 1: SYNTHETIC DATA SOURCE
# ═══════════════════════════════════════════════════════════════════════

class SyntheticDataSource(DataSource):
    """Generates synthetic factory data using statistical distributions.

    Cycle times: Normal distribution with sigma = mean * variability_factor
    Breakdowns: Weibull distribution with beta=1.8
    Status: Based on random draw against breakdown probability

    Args:
        station_configs: List of station config dicts with cycle_time, eta, beta.
        condition: Machine condition: 'good', 'average', or 'poor'.
        seed: Optional random seed for reproducibility.

    Example:
        >>> ds = SyntheticDataSource(config.stations, condition="average")
        >>> ct = ds.get_cycle_time(1)  # returns ~45.0 seconds ± variation
    """

    def __init__(self, station_configs: list, condition: str = "average",
                 seed: Optional[int] = None):
        self.station_configs = {}
        for s in station_configs:
            # Support both dataclass (with .id) and dict (with ['id'])
            sid = s.id if hasattr(s, 'id') else s['id']
            self.station_configs[sid] = s

        self.condition = condition
        self.variability = VARIABILITY_FACTORS.get(condition, 0.15)
        self.rng = np.random.default_rng(seed)

    def _get_station(self, station_id: int):
        """Get station config, supporting both dict and dataclass."""
        s = self.station_configs.get(station_id)
        if s is None:
            raise ValueError(f"Unknown station_id: {station_id}")
        return s

    def _get_attr(self, station, attr: str, default=None):
        """Get attribute from either dict or dataclass."""
        if hasattr(station, attr):
            return getattr(station, attr)
        elif isinstance(station, dict):
            return station.get(attr, default)
        return default

    def get_cycle_time(self, station_id: int) -> float:
        """Draw cycle time from Normal(mean_ct, sigma).

        sigma = mean_ct * variability_factor
        Minimum cycle time is clamped at 10% of the mean (never negative).

        Args:
            station_id: The station identifier.

        Returns:
            Cycle time in seconds.
        """
        station = self._get_station(station_id)
        mean_ct = float(self._get_attr(station, 'cycle_time_sec', 45.0))
        sigma = mean_ct * self.variability
        ct = float(self.rng.normal(mean_ct, sigma))
        return max(ct, mean_ct * 0.1)  # clamp: never below 10% of mean

    def get_station_status(self, station_id: int) -> str:
        """Determine station status based on breakdown probability.

        Returns 'broken' if random draw < breakdown_probability, else 'running'.

        Args:
            station_id: The station identifier.

        Returns:
            'running' or 'broken'
        """
        bp = self.get_breakdown_probability(station_id, utilization=0.8)
        if self.rng.random() < bp:
            return "broken"
        return "running"

    def get_breakdown_probability(self, station_id: int, utilization: float) -> float:
        """Calculate breakdown probability using Weibull distribution.

        Uses Weibull CDF: F(t) = 1 - exp(-(t/eta)^beta)
        where t is proportional to utilization.

        Args:
            station_id: The station identifier.
            utilization: Current utilization (0.0 to 1.0).

        Returns:
            Probability of breakdown (0.0 to 1.0).
        """
        station = self._get_station(station_id)
        eta = float(self._get_attr(station, 'eta_weibull', 500.0))
        beta = float(self._get_attr(station, 'beta_weibull', 1.8))

        # Scale: higher utilization → higher effective operating time
        effective_time = max(utilization, 0.01) * eta * 0.5
        prob = 1.0 - math.exp(-((effective_time / eta) ** beta))

        # Scale by condition
        condition_multiplier = {"good": 0.5, "average": 1.0, "poor": 2.0}
        prob *= condition_multiplier.get(self.condition, 1.0)

        return min(max(prob, 0.0), 1.0)


# ═══════════════════════════════════════════════════════════════════════
# IMPLEMENTATION 2: MQTT DATA SOURCE — SKELETON ONLY
# ═══════════════════════════════════════════════════════════════════════

class MQTTDataSource(DataSource):
    """MQTT-based data source for real IoT sensor data.

    REPLACE THIS WITH REAL SENSOR DATA IN PHASE 2.

    Connects to an MQTT broker and subscribes to machine topics.
    Falls back to synthetic data if no real readings are available.

    Args:
        broker_address: MQTT broker hostname or IP.
        broker_port: MQTT broker port (default 1883).
        fallback_source: SyntheticDataSource for fallback values.
    """

    def __init__(self, broker_address: str = "localhost", broker_port: int = 1883,
                 fallback_source: Optional[SyntheticDataSource] = None):
        self.broker_address = broker_address
        self.broker_port = broker_port
        self.fallback = fallback_source
        self.latest_readings: dict[int, dict] = {}
        self.connected = False

        # REPLACE THIS WITH REAL MQTT CONNECTION IN PHASE 2
        # try:
        #     import paho.mqtt.client as mqtt
        #     self.client = mqtt.Client()
        #     self.client.on_connect = self._on_connect
        #     self.client.on_message = self._on_message
        #     self.client.connect(broker_address, broker_port, 60)
        #     self.client.loop_start()
        # except Exception as e:
        #     print(f"MQTT connection failed: {e}. Using fallback.")

    def get_cycle_time(self, station_id: int) -> float:
        """REPLACE THIS WITH REAL SENSOR DATA IN PHASE 2.

        Returns latest MQTT reading or falls back to synthetic.
        """
        if station_id in self.latest_readings and "cycle_time" in self.latest_readings[station_id]:
            return self.latest_readings[station_id]["cycle_time"]
        if self.fallback:
            return self.fallback.get_cycle_time(station_id)
        return 45.0  # default fallback

    def get_station_status(self, station_id: int) -> str:
        """REPLACE THIS WITH REAL SENSOR DATA IN PHASE 2."""
        if station_id in self.latest_readings and "status" in self.latest_readings[station_id]:
            return self.latest_readings[station_id]["status"]
        if self.fallback:
            return self.fallback.get_station_status(station_id)
        return "running"

    def get_breakdown_probability(self, station_id: int, utilization: float) -> float:
        """REPLACE THIS WITH REAL SENSOR DATA IN PHASE 2."""
        if self.fallback:
            return self.fallback.get_breakdown_probability(station_id, utilization)
        return 0.02


# ═══════════════════════════════════════════════════════════════════════
# IMPLEMENTATION 3: CSV DATA SOURCE — ERP/TALLY IMPORT
# ═══════════════════════════════════════════════════════════════════════

class CSVDataSource(DataSource):
    """CSV-based data source for ERP/Tally software integration.

    REPLACE PATH WITH YOUR ERP EXPORT FOLDER IN PHASE 2.

    Watches a folder for new/updated CSV files and calculates
    effective cycle times from production data.

    CSV format: date,shift,machine_id,machine_name,parts_completed,
                downtime_minutes,operator_name

    Args:
        csv_folder: Path to the folder where ERP exports CSVs.
        fallback_source: SyntheticDataSource for fallback values.
        shift_hours: Hours per shift (for cycle time calculation).
    """

    def __init__(self, csv_folder: str = "./erp_data",
                 fallback_source: Optional[SyntheticDataSource] = None,
                 shift_hours: float = 8.0):
        self.csv_folder = csv_folder
        self.fallback = fallback_source
        self.shift_hours = shift_hours
        self.latest_readings: dict[int, dict] = {}
        self.last_update_time: dict[int, float] = {}
        self.stale_threshold_seconds = 300  # 5 minutes

        # Load any existing CSV data
        self._scan_csv_folder()

    def _scan_csv_folder(self) -> None:
        """Scan the CSV folder for data files and parse the latest rows."""
        if not os.path.exists(self.csv_folder):
            return

        for filename in os.listdir(self.csv_folder):
            if filename.endswith(".csv"):
                filepath = os.path.join(self.csv_folder, filename)
                self._parse_csv(filepath)

    def _parse_csv(self, filepath: str) -> None:
        """Parse a CSV file and update latest readings per machine."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    machine_id = int(row.get("machine_id", 0))
                    parts = int(row.get("parts_completed", 0))
                    downtime = float(row.get("downtime_minutes", 0))

                    if parts > 0:
                        # Effective cycle time = (shift_time - downtime) / parts
                        effective_ct = (self.shift_hours * 60 - downtime) * 60 / parts
                        self.latest_readings[machine_id] = {
                            "cycle_time": effective_ct,
                            "parts_completed": parts,
                            "downtime_minutes": downtime,
                            "operator_name": row.get("operator_name", ""),
                            "machine_name": row.get("machine_name", ""),
                        }
                        self.last_update_time[machine_id] = time.time()
        except Exception as e:
            print(f"Warning: Could not parse CSV {filepath}: {e}")

    def is_data_stale(self, station_id: int) -> bool:
        """Check if CSV data for a station is older than threshold."""
        if station_id not in self.last_update_time:
            return True
        age = time.time() - self.last_update_time[station_id]
        return age > self.stale_threshold_seconds

    def get_cycle_time(self, station_id: int) -> float:
        """Return cycle time from latest CSV data.

        REPLACE PATH WITH YOUR ERP EXPORT FOLDER IN PHASE 2.
        Falls back to synthetic if CSV has no data or data is stale.
        """
        if station_id in self.latest_readings and not self.is_data_stale(station_id):
            return self.latest_readings[station_id]["cycle_time"]
        if self.fallback:
            return self.fallback.get_cycle_time(station_id)
        return 45.0

    def get_station_status(self, station_id: int) -> str:
        """REPLACE PATH WITH YOUR ERP EXPORT FOLDER IN PHASE 2."""
        if self.fallback:
            return self.fallback.get_station_status(station_id)
        return "running"

    def get_breakdown_probability(self, station_id: int, utilization: float) -> float:
        """REPLACE PATH WITH YOUR ERP EXPORT FOLDER IN PHASE 2."""
        if self.fallback:
            return self.fallback.get_breakdown_probability(station_id, utilization)
        return 0.02

    def get_erp_status(self) -> dict:
        """Get the freshness status of all machine data from CSV.

        Returns:
            Dictionary with per-machine freshness info.
        """
        status = {}
        now = time.time()
        for machine_id, last_time in self.last_update_time.items():
            age_seconds = now - last_time
            status[machine_id] = {
                "last_update_seconds_ago": round(age_seconds),
                "is_fresh": age_seconds < self.stale_threshold_seconds,
                "machine_name": self.latest_readings.get(machine_id, {}).get("machine_name", ""),
            }
        return status


# ═══════════════════════════════════════════════════════════════════════
# DATA MODE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════

DATA_MODE = "synthetic"  # Options: "synthetic", "mqtt", "csv"


def get_data_source(station_configs: list, condition: str = "average",
                    seed: Optional[int] = None, **kwargs) -> DataSource:
    """Factory function to get the appropriate DataSource.

    Change DATA_MODE to switch between synthetic, MQTT, and CSV data.

    Args:
        station_configs: List of station configs.
        condition: Machine condition string.
        seed: Random seed for reproducibility.

    Returns:
        A DataSource implementation based on DATA_MODE.

    Example:
        >>> ds = get_data_source(config.stations, condition="average", seed=42)
    """
    synthetic = SyntheticDataSource(station_configs, condition, seed)

    if DATA_MODE == "mqtt":
        broker = kwargs.get("mqtt_broker", "localhost")
        return MQTTDataSource(broker_address=broker, fallback_source=synthetic)
    elif DATA_MODE == "csv":
        folder = kwargs.get("csv_folder", "./erp_data")
        return CSVDataSource(csv_folder=folder, fallback_source=synthetic)
    else:
        return synthetic
