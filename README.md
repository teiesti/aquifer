# Aquifer

Water, inferred.

**Aquifer** estimates the current storage level of a rainwater tank from publicly available rainfall data and metered outflow.

> [!WARNING]
> Aquifer is currently in an early stage of development and not yet ready for production use.
> Many features are still missing or subject to change without prior notice.
> Use at your own risk!

## Concept

Without a level sensor, a buried or opaque rainwater tank is like a geological [aquifer](https://en.wikipedia.org/wiki/Aquifer).
You cannot observe its contents directly, but you *can* estimate its state from water entering and leaving it.

```
Storage(t) = clamp(Storage(t-1) + Inflow(t) - Outflow(t), 0, Capacity)
```

Aquifer applies this simple [mass balance](https://en.wikipedia.org/wiki/Mass_balance) using the following assumptions about inflow and outflow.

### Inflow comes from precipitation

Inflow can be estimated from the rain falling on the collection area of the tank.

```
Inflow(t) = Precipitation(t) * Collection Area
```

Inflow is measured in liters, precipitation in millimeters, and collection area in square meters.

Hourly precipitation data from nearby weather stations is available for free at [Meteostat](https://meteostat.net/).
No rain sensor is needed.

### Outflow is metered

Water leaving the tank is metered via a discharge line meter.
Aquifer supports devices exposing a cumulative meter reading via HTTP, like the [wasserleser](https://stromleser.de/products/wasserleser).

Aquifer periodically polls the meter and stores the reading in a local database.
Outflow is derived from the difference between consecutive readings.

```
Outflow(t) = Reading(t) - Reading(t-1)
```

We assume the readings are monotonically non-decreasing (each reading is greater than or equal to the previous one); meter resets or rollovers must be detected and handled separately.

## Getting Started

### Prerequisites

- Python 3.12 or later
- A [Meteostat](https://meteostat.net/) weather station near your cistern
- A water meter exposing a cumulative reading via HTTP (e.g. [wasserleser](https://stromleser.de/products/wasserleser))

### Installation

Install Aquifer directly from GitHub using pip:

```sh
pip install git+https://github.com/teiesti/aquifer.git
```

### Configuration

Copy [aquifer.toml.example](aquifer.toml.example) and adjust it to your setup:

```sh
cp aquifer.toml.example aquifer.toml
```

Aquifer will look for a configuration in

- `./aquifer.toml`,
- `~/.config/aquifer/aquifer.toml`, and
- `/etc/aquifer/aquifer.toml`.

## Usage

Run `aquifer --help` for a full list of commands and options.

Once configured, start polling your water meter in the background:

```sh
aquifer meter poll --record --watch
```

This periodically reads the meter and stores each reading in the local database.

To estimate the current tank storage level:

```sh
aquifer tank history
```

To inspect recorded meter readings or fetched precipitation data:

```sh
aquifer meter history
aquifer rain history
```

To start the interactive dashboard (requires optional dependencies):

```sh
pip install "aquifer[dashboard] @ git+https://github.com/teiesti/aquifer.git"
aquifer dashboard
```

## License

Aquifer is distributed under the terms of the MIT license.
See [LICENSE](LICENSE) for details!

Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in Aquifer by you shall be licensed as above, without any additional terms or conditions.
