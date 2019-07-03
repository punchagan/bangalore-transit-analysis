#!/usr/bin/env python3
from datetime import datetime, timedelta
import json
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


if __name__ == "__main__":
    dump_ward_pairs()
