# Aquifer

Water, inferred.

**Aquifer** estimates the current storage level of a rainwater tank from publicly available rainfall data and metered outflow.

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

## Installation

TODO

## Usage

TODO

## License

Aquifer is distributed under the terms of the MIT license.
See [LICENSE](LICENSE) for details!

Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in Aquifer by you shall be licensed as above, without any additional terms or conditions.
