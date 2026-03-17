import dash_mantine_components as dmc  # type: ignore
from dash import Dash

from aquifer.configuration import Configuration
from aquifer.estimation import Estimation


def serve_layout():
    config = Configuration.find()
    estimation = Estimation(config)

    level = estimation.storage["level"].iloc[-1] * 100
    storage = estimation.storage["storage"].iloc[-1]
    capacity = config.tank.capacity

    return dmc.MantineProvider(
        dmc.AppShell(
            [
                dmc.AppShellHeader(
                    dmc.Group(
                        [
                            dmc.Title("Aquifer", c="blue"),
                        ],
                        h="100%",
                        px="md",
                    )
                ),
                dmc.AppShellMain(f"{level:.0f} % ({storage:.0f} / {capacity:.0f})"),
            ],
            header={"height": 60},
            padding="md",
        )
    )


app = Dash(title="Aquifer")
app.layout = serve_layout
