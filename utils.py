import json
from os.path import abspath, dirname, join

import pandas as pd
from shapely.geometry import shape, Point

HERE = dirname(abspath(__file__))
DATA = join(HERE, "data")
WARD_SHAPES = []


def get_bmtc_routes(source="routes.2018.csv"):
    # Read the BMTC Route data
    return pd.read_csv(join(DATA, source))


def get_uber_travel_time(quarter="2018-4"):
    # Read Travel Time Data provided by Uber
    # They provide mean travel time between "wards"
    path = join(
        DATA, "bangalore-wards-{}-All-HourlyAggregate.csv".format(quarter)
    )
    return pd.read_csv(path)


def get_wards():
    # Read the ward boundaries data from Uber
    with open(join(DATA, "bangalore_wards.json")) as f:
        wards = json.load(f)

    return wards


def get_ward_shapes():
    wards = get_wards()
    ward_shapes = [
        (
            shape(feature["geometry"]),
            int(feature["properties"]["WARD_NO"]),
            feature["properties"]["WARD_NAME"],
        )
        for feature in wards["features"]
    ]
    return ward_shapes


def get_ward(lat_lng):
    """Return ward that contains a given point (lat, lng).   """

    global WARD_SHAPES
    if not WARD_SHAPES:
        WARD_SHAPES = get_ward_shapes()

    # NOTE: The WARD_SHAPES are in (lng, lat).
    # So, we swap co-ordinates on the point.
    p = Point([float(x) for x in lat_lng][::-1])
    for ward_shape, ward_id, ward_name in WARD_SHAPES:
        if ward_shape.contains(p):
            return ward_id, ward_name

    return (None, None)


def route_to_wards(route):
    """List of wards for the bus-stops in a route.

    The function de-duplicates wards, and only returns unique wards.
    """
    bus_stops = json.loads(route.map_json_content)
    wards = [get_ward(bus_stop["latlons"]) for bus_stop in bus_stops]
    return sorted(set(wards), key=lambda x: wards.index(x))
