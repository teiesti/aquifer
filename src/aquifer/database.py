"""Database abstraction layer for storing meter readings."""

import sqlite3
from datetime import timezone
from typing import Callable, Self

import pandas as pd

from aquifer.meter import Reading


class Readings:
    """Repository for meter readings stored in a SQLite database."""

    _get_connection: Callable[[], sqlite3.Connection]

    def __init__(self, get_connection: Callable[[], sqlite3.Connection]):
        self._get_connection = get_connection

    def initialize(self) -> None:
        """Create the readings table if it does not already exist."""
        self._get_connection().execute(
            """
            CREATE TABLE IF NOT EXISTS readings (
                timestamp TEXT PRIMARY KEY,
                total_consumption REAL NOT NULL
            )
            """
        )

    def add(self, reading: Reading) -> None:
        """Insert or replace a reading in the database.

        Args:
            reading: The meter reading to persist.

        Raises:
            ValueError: If ``reading.timestamp`` is a naive datetime with no timezone info.
        """
        if reading.timestamp.tzinfo is None:
            raise ValueError("reading.timestamp must be timezone-aware")
        self._get_connection().execute(
            "INSERT OR REPLACE INTO readings (timestamp, total_consumption) VALUES (?, ?)",
            (reading.timestamp.astimezone(timezone.utc).isoformat(), reading.total_consumption),
        )

    def all(self) -> pd.DataFrame:
        """Return all readings ordered by timestamp ascending.

        Returns:
            A DataFrame indexed by timestamp with a ``total_consumption`` column.
        """
        return pd.read_sql_query(
            "SELECT timestamp, total_consumption FROM readings ORDER BY timestamp ASC",
            self._get_connection(),
            parse_dates={"timestamp": {"utc": True}},
            index_col="timestamp",
        )


class Database:
    """Context manager for a SQLite database connection."""

    _path: str
    _connection: sqlite3.Connection | None = None

    def __init__(self, path: str):
        self._path = path

    def __enter__(self) -> Self:
        self._connection = sqlite3.connect(self._path)
        try:
            self._connection.execute("PRAGMA foreign_keys=ON")
            self._connection.execute("PRAGMA busy_timeout=5000")
        except Exception:
            self._connection.close()
            self._connection = None
            raise
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._connection is None:
            raise RuntimeError("Use 'with Database(...) as db:'")
        try:
            if exc_type is None:
                self._connection.commit()
            else:
                self._connection.rollback()
        finally:
            self._connection.close()
            self._connection = None

    @property
    def connection(self) -> sqlite3.Connection:
        """Return the active SQLite connection.

        Raises:
            RuntimeError: If accessed outside of a ``with`` block.
        """
        if self._connection is None:
            raise RuntimeError("Use 'with Database(...) as db:'")
        return self._connection

    @property
    def readings(self) -> Readings:
        """Return the readings repository backed by the active connection."""
        return Readings(lambda: self.connection)
