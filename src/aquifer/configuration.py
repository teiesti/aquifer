"""Configuration parser for aquifer."""

import tomllib
from dataclasses import dataclass
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
class Configuration:
    """Top-level aquifer configuration loaded from a TOML file."""

    meter: Meter
    database: Database

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
