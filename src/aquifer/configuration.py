"""Configuration parser for aquifer."""

import tomllib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Self

from aquifer.meter import Driver as MeterDriver


@dataclass
class Meter:
    """Configuration for the discharge line meter."""

    driver: MeterDriver
    endpoint: str
    poll_interval: int


@dataclass
class Database:
    """Configuration for the SQLite database used to store readings."""

    path: str


@dataclass
class Location:
    """Geographic coordinates of the rainwater tank, used for fetching weather data."""

    latitude: float
    longitude: float
    elevation: int


@dataclass
class Stations:
    """Search criteria for nearby weather stations."""

    radius: int
    limit: int


@dataclass
class Tank:
    """Physical characteristics of the rainwater tank, used for storage estimation."""

    capacity: float
    collection_area: float


@dataclass
class InitialState:
    """Initial state of the rainwater tank at the start of the simulation."""

    timestamp: datetime
    storage: float


@dataclass
class Configuration:
    """Top-level aquifer configuration loaded from a TOML file."""

    meter: Meter
    database: Database
    location: Location
    stations: Stations
    tank: Tank
    initial_state: InitialState

    @classmethod
    def load(cls, path: str | Path) -> Self:
        """Load a configuration from a TOML file.

        Args:
            path: Path to the TOML configuration file.

        Returns:
            A Configuration instance populated from the file.

        Raises:
            FileNotFoundError: If the file does not exist.
            tomllib.TOMLDecodeError: If the file is not valid TOML.
            KeyError: If required configuration keys are missing.
            ValueError: If the meter driver value is not supported.
            TypeError: If the database configuration contains unexpected keys.
        """
        with open(path, "rb") as file:
            data = tomllib.load(file)

        return cls(
            meter=Meter(
                driver=MeterDriver(data["meter"]["driver"]),
                endpoint=data["meter"]["endpoint"],
                poll_interval=data["meter"]["poll_interval"],
            ),
            database=Database(**data["database"]),
            location=Location(**data["location"]),
            stations=Stations(**data["stations"]),
            tank=Tank(**data["tank"]),
            initial_state=InitialState(
                timestamp=datetime.fromisoformat(data["initial_state"]["timestamp"]).astimezone(timezone.utc),
                storage=data["initial_state"]["storage"],
            ),
        )

    _SEARCH_PATHS = [
        Path("aquifer.toml"),
        Path("~/.config/aquifer/aquifer.toml"),
        Path("/etc/aquifer/aquifer.toml"),
    ]

    @classmethod
    def find(cls) -> Self:
        """Search default locations for a configuration file and load it.

        Returns:
            A Configuration instance from the first configuration file found.

        Raises:
            FileNotFoundError: If no configuration file is found in the default search paths.
        """
        for path in cls._SEARCH_PATHS:
            resolved = path.expanduser()

            if resolved.is_file():
                return cls.load(resolved)

        searched = ", ".join(f"'{p}'" for p in cls._SEARCH_PATHS)
        raise FileNotFoundError(f"No configuration file found. Searched: {searched}")
