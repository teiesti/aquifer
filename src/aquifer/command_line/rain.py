"""Command-line interface for fetching precipitation data from nearby weather stations."""

from datetime import datetime

import typer

from aquifer.configuration import Configuration
from aquifer.precipitation import Gauge

app = typer.Typer(help="External precipitation data fetched from nearby weather stations.")


@app.command()
def history() -> None:
    """Display the history of precipitation data fetched from nearby weather stations."""
    config = Configuration.find()
    gauge = Gauge(
        config.location.latitude,
        config.location.longitude,
        config.location.elevation,
        config.stations.radius,
        config.stations.limit,
    )

    start = config.initial_state.timestamp
    end = datetime.now().astimezone()
    local_tz = end.tzinfo

    df = gauge.fetch(start, end).tz_convert(local_tz)

    typer.echo(df)
