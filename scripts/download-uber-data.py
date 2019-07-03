#!/usr/bin/env python3
from datetime import datetime, timedelta
import json
import os
from os.path import abspath, dirname, join, exists
import sys

import pandas as pd
import requests

HERE = dirname(abspath(__file__))
SRC = join(HERE, "..")
DATA = join(SRC, "data")

sys.path.insert(0, SRC)
from utils import get_bmtc_routes, route_to_wards, get_wards


def dump_ward_pairs(include_reverse=True):
    """Get list of all ward pairs between which we want transit time.

    If include_reverse is True, the reverse ward pairs are also added to the
    list of ward pairs. This is useful for computing the "up" and "down"
    transit time for a route.

    """

    dump_path = join(DATA, "ward-pairs.json")
    if exists(dump_path):
        with open(dump_path) as f:
            return json.load(f)

    data = get_bmtc_routes()
    print("Dumping pairs of wards for {} bus routes ".format(len(data)))
    wards = get_wards()
    ward_properties = {
        int(ward["properties"]["WARD_NO"]): ward["properties"]
        for ward in wards["features"]
    }

    ward_pairs = set()
    for row in data.index:
        route = data.loc[row]
        try:
            w = route_to_wards(route)
            pairs = zip(w[:-1], w[1:])
            ward_pairs.update(pairs)
        except TypeError:
            pass

    movement_pairs = []
    for (src_id, _), (dst_id, _) in ward_pairs:
        if src_id is None or dst_id is None:
            continue
        src_movement_id = ward_properties[src_id]["MOVEMENT_ID"]
        dst_movement_id = ward_properties[dst_id]["MOVEMENT_ID"]
        pair = ((src_id, src_movement_id), (dst_id, dst_movement_id))
        movement_pairs.append(pair)
        if include_reverse:
            movement_pairs.append(pair[::-1])

    with open(dump_path, "w") as f:
        json.dump(movement_pairs, f, indent=2)

    return movement_pairs


def get_travel_time(
    src, dst, time_range=None, time_period="ALL_DAY", days_of_week=None
):
    """Fetch travel time between a source and a destination.

    src and dst are Movement IDs for wards. These can be obtained from the ward
    boundaries dataset provided by Uber.

    The function uses API calls to Uber's backend, and you need to set a couple
    of environment variables for this function to work - MOVEMENT_WEB_COOKIE
    and MOVEMENT_CSRF_TOKEN. These can be obtained by visiting
    movement.uber.com in your browser and Network tab of the developer console
    in your browser.

    """

    if days_of_week is None:
        days_of_week = [1, 2, 3, 4, 5, 6, 7]

    if time_range:
        start, end = time_range
    else:
        delta = timedelta(seconds=19800)
        start = int((datetime(2018, 10, 1) + delta).strftime("%s"))
        end = int((datetime(2018, 12, 31) + delta).strftime("%s"))

    cookies = {"web-movement:sess": os.environ["MOVEMENT_WEB_COOKIE"]}
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0",
        "x-csrf-token": os.environ["MOVEMENT_CSRF_TOKEN"],
        "Content-Type": "application/json",
    }
    params = (("rpc", "GET_DETAILED_TRAVEL_TIMES"),)
    data = {
        "query": {
            "cityId": 130,
            "sourceId": src,
            "dataSet": "wards",
            "destinationId": dst,
            "timeRanges": [{"startTime": start, "endTime": end}],
            "daysOfWeek": days_of_week,
            "timePeriodBucket": time_period,
        }
    }

    response = requests.post(
        "https://movement.uber.com/_rpc",
        headers=headers,
        params=params,
        cookies=cookies,
        data=json.dumps(data),
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    return response.json()["data"]


def download_uber_travel_time_data():
    pairs = dump_ward_pairs()
    print("Fetching travel time for {} pairs".format(len(pairs)))

    travel_time_data = dict()
    for i, ((src_w_id, src_m_id), (dst_w_id, dst_m_id)) in enumerate(pairs):
        travel_time = get_travel_time(src_m_id, dst_m_id)
        print(i, (src_w_id, dst_w_id))
        travel_time_data["{}-{}".format(src_w_id, dst_w_id)] = travel_time

    path = join(DATA, "uber-travel-time-data.json")
    with open(path, "w") as f:
        json.dump(travel_time_data, f, indent=2)


if __name__ == "__main__":
    download_uber_travel_time_data()
