"""Client for the discharge line meter."""

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
    """A single meter reading containing a timestamp and total consumption."""

    timestamp: datetime
    total_consumption: float


class Driver(str, Enum):
    """Supported meter driver implementations."""

    WASSERLESER = "wasserleser"


class Meter:
    """Client for reading data from a discharge line meter."""

    _driver: Driver
    _endpoint: str

    def __init__(self, driver: Driver, endpoint: str):
        self._driver = driver
        self._endpoint = endpoint

    def read(self) -> Reading:
        """Fetch the current reading from the meter endpoint.

        Returns:
            A Reading with the timestamp reported by the meter and total consumption in liters.

        Raises:
            requests.HTTPError: If the HTTP request to the endpoint fails.
            NotImplementedError: If the configured driver is not supported.
            ValueError: If the response data cannot be parsed.
        """
        response = requests.get(self._endpoint, timeout=10)
        response.raise_for_status()

        match self._driver:
            case Driver.WASSERLESER:
                data = response.json()
                try:
                    return Reading(
                        timestamp=datetime.fromtimestamp(int(data["timestamp"]), tz=timezone.utc),
                        total_consumption=_m3_string_to_liters(data["total_consumption"]),
                    )
                except (KeyError, TypeError) as exc:
                    raise ValueError("Invalid response schema from meter endpoint") from exc

            case _:
                raise NotImplementedError(f"Unsupported driver: {self._driver}")
