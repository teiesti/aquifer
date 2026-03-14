from aquifer.configuration import Configuration, MeterDriver


def test_configuration_load(pytestconfig):
    config = Configuration.load(pytestconfig.rootpath / "aquifer.toml.example")

    assert config.meter.driver == MeterDriver.WASSERLESER
    assert config.meter.endpoint == "http://wasserleser/v1/data"
    assert config.meter.poll_interval == 300

    assert config.database.path == "aquifer.db"
