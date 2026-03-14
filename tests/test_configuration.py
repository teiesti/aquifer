from datetime import datetime

from aquifer.configuration import Configuration, MeterDriver


def test_configuration_load(pytestconfig):
    config = Configuration.load(pytestconfig.rootpath / "aquifer.toml.example")

    assert config.meter.driver == MeterDriver.WASSERLESER
    assert config.meter.endpoint == "http://wasserleser/v1/data"
    assert config.meter.poll_interval == 300

    assert config.database.path == "aquifer.db"

    assert config.location.latitude == 52.278889
    assert config.location.longitude == 8.043056
    assert config.location.elevation == 63

    assert config.stations.radius == 20000
    assert config.stations.limit == 5

    assert config.tank.capacity == 10000.0
    assert config.tank.collection_area == 100.0

    assert config.initial_state.timestamp == datetime.fromisoformat("2026-01-01T00:00:00+01:00")
    assert config.initial_state.storage == 5000.0
