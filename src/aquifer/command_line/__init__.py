"""Command-line interface for the Aquifer application."""

from typing import Annotated

import typer

from . import meter, rain, tank

app = typer.Typer(help="Rainwater tank storage estimation using rainfall data and metered water use.")

app.add_typer(meter.app, name="meter")
app.add_typer(rain.app, name="rain")
app.add_typer(tank.app, name="tank")


@app.command()
def dashboard(
    debug: Annotated[bool, typer.Option("--debug", help="Run the dashboard in debug mode.")] = False,
    host: Annotated[str, typer.Option("--host", help="Host to bind the dashboard server to.")] = "127.0.0.1",
) -> None:
    """Start the dashboard."""
    try:
        from aquifer.dashboard import app as dashboard_app  # noqa: PLC0415
    except ImportError as e:
        typer.echo(
            "The dashboard requires optional dependencies that are not installed.\n"
            "Please install them with:\n"
            "    pip install aquifer[dashboard]"
        )
        raise typer.Exit(code=1) from e

    dashboard_app.run(debug=debug, host=host)
