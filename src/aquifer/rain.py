from datetime import datetime, timezone

import meteostat as ms
import pandas as pd


class Gauge:
    _point: ms.Point
    _stations: pd.DataFrame

    def __init__(self, latitude: float, longitude: float, elevation: int, radius: int, limit: int) -> None:
        self._point = ms.Point(latitude, longitude, elevation)
        self._stations = ms.stations.nearby(self._point, radius=radius, limit=limit)

    def fetch(self, start: datetime, end: datetime) -> pd.DataFrame:
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
