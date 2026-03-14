"""Command-line interface for managing water meter readings."""

import time
from typing import Annotated

import typer

from aquifer.configuration import Configuration
from aquifer.database import Database
from aquifer.meter import Meter

app = typer.Typer(help="Persisted discharge measurements polled from the water meter.")


@app.command()
def poll(
    record: Annotated[bool, typer.Option("--record", help="Persist the polled reading to the database.")] = False,
    watch: Annotated[bool, typer.Option("--watch", help="Poll continuously at a regular interval.")] = False,
) -> None:
    """Poll the water meter for the current discharge measurement."""
    config = Configuration.find()
    meter = Meter(config.meter.driver, config.meter.endpoint)

    def poll_once() -> None:
        try:
            reading = meter.poll()
            typer.echo(f"{reading.timestamp.astimezone().isoformat()}, {reading.total_consumption}")
            if record:
                with Database(config.database.path) as db:
                    db.readings.initialize()
                    db.readings.add(reading)
        except Exception as e:
            typer.echo(f"Error: Polling failed: {e}", err=True)

    scheduled = time.monotonic()
    poll_once()

    if watch:
        try:
            while True:
                scheduled += config.meter.poll_interval
                sleep = scheduled - time.monotonic()

                if sleep > 0:
                    time.sleep(sleep)
                else:
                    typer.echo(
                        f"Warning: Polling is behind schedule by {-sleep:.2f} seconds. "
                        "Consider increasing the poll interval.",
                        err=True,
                    )

                poll_once()

        except KeyboardInterrupt as e:
            raise typer.Exit(code=0) from e
