from datetime import datetime, timezone
from functools import cached_property

import pandas as pd

from aquifer.configuration import Configuration
from aquifer.database import Database
from aquifer.rain import Gauge


def clamp(value: float, min: float, max: float) -> float:
    if value < min:
        return min
    elif value > max:
        return max
    else:
        return value


class Estimation:
    _configuration: Configuration

    def __init__(self, configuration: Configuration) -> None:
        self._configuration = configuration

    @cached_property
    def start(self) -> datetime:
        return self._configuration.initial_state.timestamp

    @cached_property
    def end(self) -> datetime:
        return datetime.now().astimezone(timezone.utc)

    @cached_property
    def inflow(self) -> pd.DataFrame:
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
        with Database(self._configuration.database.path) as db:
            df = db.readings.all()

        index = pd.date_range(self.start, self.end, freq="h")
        df = df.reindex(index, method="ffill")
        df["outflow"] = df["total_consumption"].diff().fillna(0)

        return df

    @cached_property
    def storage(self) -> pd.DataFrame:
        df = self.inflow.join(self.outflow, how="right")

        current_storage = self._configuration.initial_state.storage

        def storage(row):
            nonlocal current_storage
            current_storage = clamp(
                current_storage + row["inflow"] - row["outflow"], 0, self._configuration.tank.capacity
            )
            return current_storage

        df["storage"] = df.apply(storage, axis=1)
        df["level"] = df["storage"] / self._configuration.tank.capacity

        return df
