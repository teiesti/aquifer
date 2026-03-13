from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

import requests


def _m3_string_to_liters(s: str) -> float:
    match s.strip().split():
        case [value_str, "m3"]:
            return float(value_str) * 1000

        case _:
            raise ValueError(f"Expected '<value> m3' with exactly two whitespace-separated tokens, got: {s!r}")


@dataclass
class Reading:
    timestamp: datetime
    total_consumption: float


class Driver(str, Enum):
    WASSERLESER = "wasserleser"


class Meter:
    _driver: Driver
    _endpoint: str

    def __init__(self, driver: Driver, endpoint: str):
        self._driver = driver
        self._endpoint = endpoint

    def read(self) -> Reading:
        response = requests.get(self._endpoint, timeout=10)
        response.raise_for_status()

        match self._driver:
            case Driver.WASSERLESER:
                data = response.json()
                return Reading(
                    timestamp=datetime.fromtimestamp(int(data["timestamp"]), tz=timezone.utc),
                    total_consumption=_m3_string_to_liters(data["total_consumption"]),
                )

            case _:
                raise NotImplementedError(f"Unsupported driver: {self._driver}")
