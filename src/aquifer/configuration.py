import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Self

from aquifer.meter import Driver as MeterDriver


@dataclass
class Meter:
    driver: MeterDriver
    endpoint: str
    poll_interval: int


@dataclass
class Database:
    path: str


@dataclass
class Configuration:
    meter: Meter
    database: Database

    @classmethod
    def load(cls, path: str | Path) -> Self:
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
        for path in cls._SEARCH_PATHS:
            resolved = path.expanduser()

            if resolved.exists():
                return cls.load(resolved)

        searched = ", ".join(f"'{p}'" for p in cls._SEARCH_PATHS)
        raise FileNotFoundError(f"No configuration file found. Searched: {searched}")
