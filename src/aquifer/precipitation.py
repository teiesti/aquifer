"""Precipitation data retrieval using the meteostat weather data service."""

from datetime import datetime, timezone

import meteostat as ms
import pandas as pd


class PrecipitationGauge:
    """Fetches historical hourly precipitation data for a geographic location.

    Queries nearby weather stations via the meteostat service and interpolates
    the results to the given coordinates.
    """

    _point: ms.Point
    _stations: pd.DataFrame

    def __init__(self, latitude: float, longitude: float, elevation: int, radius: int, limit: int) -> None:
        self._point = ms.Point(latitude, longitude, elevation)
        self._stations = ms.stations.nearby(self._point, radius=radius, limit=limit)

    def fetch(self, start: datetime, end: datetime) -> pd.DataFrame:
        """Fetch hourly precipitation data for the configured location and time range.

        Args:
            start: Start of the time range (timezone-aware datetime).
            end: End of the time range (timezone-aware datetime).

        Returns:
            A DataFrame indexed by timestamp (UTC) with a ``precipitation`` column
            containing hourly precipitation amounts in millimetres.

        Raises:
            ValueError: If no precipitation data is available for the specified
                location and time range.
        """
        ts = ms.hourly(
            station=self._stations,
            start=start.astimezone(timezone.utc),
            end=end.astimezone(timezone.utc),
            timezone="utc",
            parameters=[ms.Parameter.PRCP],
        )
        df = ms.interpolate(ts, self._point).fetch()

        if df is None:
            raise ValueError("No precipitation data available for the specified location and time range.")

        return df.rename(columns={"prcp": "precipitation"})
