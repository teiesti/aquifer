"""Command-line interface for the Aquifer application."""

import typer

from . import meter

app = typer.Typer(help="Rainwater tank storage estimation using rainfall data and metered water use.")

app.add_typer(meter.app, name="meter")
