"""Tank storage estimation based on inflow and outflow data."""

from datetime import datetime, timezone
from functools import cached_property

import pandas as pd

from aquifer.configuration import Configuration
from aquifer.database import Database
from aquifer.rain import Gauge


def clamp(value: float, min_value: float, max_value: float) -> float:
    """Clamp a value to the given range.

    Args:
        value: The value to clamp.
        min_value: The minimum allowed value.
        max_value: The maximum allowed value.

    Returns:
        ``value`` clamped to ``[min_value, max_value]``.
    """
    if value < min_value:
        return min_value

    if value > max_value:
        return max_value

    return value


class Estimation:
    """Estimates tank storage history from inflow (rain) and outflow (meter) data."""

    _configuration: Configuration

    def __init__(self, configuration: Configuration) -> None:
        self._configuration = configuration

    @cached_property
    def start(self) -> datetime:
        """Return the start of the estimation period.

        Returns:
            The timestamp of the initial state as stored in the configuration.
        """
        return self._configuration.initial_state.timestamp

    @cached_property
    def end(self) -> datetime:
        """Return the end of the estimation period.

        Returns:
            The current time in UTC.
        """
        return datetime.now().astimezone(timezone.utc)

    @cached_property
    def inflow(self) -> pd.DataFrame:
        """Fetch and compute hourly inflow from precipitation data.

        Returns:
            A DataFrame indexed by hour with ``precipitation`` and ``inflow``
            columns, where ``inflow`` is precipitation multiplied by the tank
            collection area.
        """
        df = Gauge(
            self._configuration.location.latitude,
            self._configuration.location.longitude,
            self._configuration.location.elevation,
            self._configuration.stations.radius,
            self._configuration.stations.limit,
        ).fetch(self.start, self.end)

        df.fillna(0, inplace=True)
        df["inflow"] = df["precipitation"] * self._configuration.tank.collection_area

        return df

    @cached_property
    def outflow(self) -> pd.DataFrame:
        """Load and compute hourly outflow from meter readings.

        Returns:
            A DataFrame indexed by hour with ``total_consumption`` and
            ``outflow`` columns, where ``outflow`` is the hourly difference in
            total consumption.
        """
        with Database(self._configuration.database.path) as db:
            db.readings.initialize()
            df = db.readings.all()

        index = pd.date_range(self.start, self.end, freq="h")
        df = df.reindex(index, method="ffill")
        df["outflow"] = df["total_consumption"].diff().fillna(0)

        return df

    @cached_property
    def storage(self) -> pd.DataFrame:
        """Compute the hourly tank storage history.

        Returns:
            A DataFrame indexed by hour with ``storage`` (litres) and ``level``
            (fraction of capacity) columns derived from inflow and outflow.
        """
        df = self.inflow.join(self.outflow, how="right")

        current = self._configuration.initial_state.storage
        capacity = self._configuration.tank.capacity
        values = []

        inflow_arr = df["inflow"].to_numpy(dtype=float)
        outflow_arr = df["outflow"].to_numpy(dtype=float)

        for inflow_val, outflow_val in zip(inflow_arr, outflow_arr, strict=True):
            current = clamp(current + inflow_val - outflow_val, 0, capacity)
            values.append(current)

        df["storage"] = values
        df["level"] = df["storage"] / capacity

        return df
