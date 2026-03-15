"""Command-line interface for estimating tank storage."""

from datetime import datetime

import typer

from aquifer.configuration import Configuration
from aquifer.estimation import Estimation

app = typer.Typer(help="Inferred tank storage state calculated from inflow and outflow.")


@app.command()
def history() -> None:
    """Display the history of inferred tank storage levels."""
    config = Configuration.find()
    estimation = Estimation(config)
    local_tz = datetime.now().astimezone().tzinfo
    df = estimation.storage.tz_convert(local_tz)
    typer.echo(df)
