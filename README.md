# bangalore-transit-analysis

Bangalore Transit data analysis

## v0.1

The first version attempts to audit estimated travel times of buses in BMTC
schedules. Uber provides data for transit times between different wards in
Bangalore, and an attempt was made to use this data for the validation.

[This
notebook](https://github.com/punchagan/bangalore-transit-analysis/blob/v0.1/Audit%20BMTC%20bus%20schedules%20using%20Uber%20Travel%20Time%20data.ipynb) (or [this presentation](https://github.com/punchagan/bangalore-transit-analysis/releases/download/v0.1/uber-data-problems.pdf))
explains the approach taken and the problems we found in Uber's data.

### Data

The data required to run the notebook is available
[here](https://github.com/punchagan/bangalore-transit-analysis/releases/tag/v0.1).

- The `bangalore-wards-201*-*-All-HourlyAggregate.csv*` files have been
  downloaded from movement.uber.com.

- `bangalore_wards.json` has also been downloaded from movement.uber.com and is
  required to be able to interpret the ward numbers used in the csv files.

- `routes.csv` is data scraped from the BMTC site, provided by the organisers of
  [this DataKind meetup](https://www.meetup.com/DataKind-Bangalore/events/262356567/).
