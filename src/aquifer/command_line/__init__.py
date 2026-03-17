"""Command-line interface for the Aquifer application."""

from typing import Annotated

import typer

from aquifer.dashboard import app as dashboard_app

from . import meter, rain, tank

app = typer.Typer(help="Rainwater tank storage estimation using rainfall data and metered water use.")

app.add_typer(meter.app, name="meter")
app.add_typer(rain.app, name="rain")
app.add_typer(tank.app, name="tank")


@app.command()
def dashboard(
    debug: Annotated[bool, typer.Option("--debug", help="Run the dashboard in debug mode.")] = False,
) -> None:
    """Start the dashboard."""
    dashboard_app.run(debug=debug)
