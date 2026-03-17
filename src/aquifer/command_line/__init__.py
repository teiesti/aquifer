"""Command-line interface for the Aquifer application."""

import typer

from . import meter, rain, tank

app = typer.Typer(help="Rainwater tank storage estimation using rainfall data and metered water use.")

app.add_typer(meter.app, name="meter")
app.add_typer(rain.app, name="rain")
app.add_typer(tank.app, name="tank")
