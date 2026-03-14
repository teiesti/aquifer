"""Command-line interface for fetching precipitation data from nearby weather stations."""

from datetime import datetime

import meteostat as ms
import typer

from aquifer.configuration import Configuration

app = typer.Typer(help="External precipitation data fetched from nearby weather stations.")


@app.command()
def history() -> None:
    """Display the history of precipitation data fetched from nearby weather stations."""
    config = Configuration.find()

    point = ms.Point(config.location.latitude, config.location.longitude, config.location.elevation)
    stations = ms.stations.nearby(point, radius=config.stations.radius, limit=config.stations.limit)

    start = config.initial_state.timestamp
    end = datetime.now().astimezone()

    local_tz = end.tzinfo

    ts = ms.hourly(stations, start, end, timezone="utc", parameters=[ms.Parameter.PRCP])
    df = ms.interpolate(ts, point).fetch()

    typer.echo(df.tz_convert(local_tz))
