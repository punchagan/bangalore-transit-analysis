import json
from os.path import abspath, dirname, join

import pandas as pd
from shapely.geometry import shape, Point

HERE = dirname(abspath(__file__))
DATA = join(HERE, "data")
WARD_SHAPES = []
UBER_TRAVEL_TIMES = None


def get_bmtc_routes(source="routes.2018.csv"):
    # Read the BMTC Route data
    return pd.read_csv(join(DATA, source))


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
    try:
        bus_stops = json.loads(route.map_json_content)
    except TypeError:
        return []
    wards = [get_ward(bus_stop["latlons"]) for bus_stop in bus_stops]
    return sorted(set(wards), key=lambda x: wards.index(x))


def read_uber_travel_time():
    global UBER_TRAVEL_TIMES
    if not UBER_TRAVEL_TIMES:
        path = join(DATA, "uber-travel-time-data.json")
        with open(path) as f:
            UBER_TRAVEL_TIMES = json.load(f)

    return UBER_TRAVEL_TIMES


def mean_time(src, dst):
    key = "{}-{}".format(src, dst)
    data = UBER_TRAVEL_TIMES.get(key)
    if not data:
        return None
    data = [day["meanTravelTimeSec"] for day in data[0]["daily"].values()]
    return sum(data) / len(data)


def mean_route_time(wards):
    pairs = zip(wards[:-1], wards[1:])
    route_time = 0
    for (src_id, _), (dst_id, _) in pairs:
        time = mean_time(src_id, dst_id)
        if time is not None:
            route_time += time
    return route_time


def estimate_travel_time(route):
    read_uber_travel_time()
    wards = route_to_wards(route)
    means = pd.Series(mean_route_time(wards))
    missing_data = means.hasnans
    total_minutes = int(means.sum() / 60)
    hours = int(total_minutes / 60)
    minutes = total_minutes % 60
    return (hours, minutes), missing_data
