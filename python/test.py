#!/usr/bin/env python3

# For interactive shell
import readline
import code

import json
from lib.pos import Pos
from lib.zone import Zone
from lib.zone_manager import ZoneManager

tests = {}


with open("../config/region_1.json", "r") as fp:
    region_1_prop = json.load(fp)
    fp.close()

tests["region_1"] = ZoneManager(region_1_prop["locationBounds"])


with open("../config/region_2.json", "r") as fp:
    region_2_prop = json.load(fp)
    fp.close()

tests["region_2"] = ZoneManager(region_2_prop["locationBounds"])


tests["test_3d_mid"] = ZoneManager([
    {
        "name": "Alice",
        "type": "Eggs",
        "pos1": [2, 2, 2],
        "pos2": [4, 4, 4],
    },
    {
        "name": "Bob",
        "type": "Spam",
        "pos1": [1, 1, 1],
        "pos2": [5, 5, 5],
    },
])


tests["test_2d_mid"] = ZoneManager([
    {
        "name": "Alice",
        "type": "Eggs",
        "pos1": [2, 2],
        "pos2": [4, 4],
    },
    {
        "name": "Bob",
        "type": "Spam",
        "pos1": [1, 1],
        "pos2": [5, 5],
    },
], axis_order=[1, 0])


tests["test_2d_corner"] = ZoneManager([
    {
        "name": "Alice",
        "type": "Eggs",
        "pos1": [1, 2],
        "pos2": [3, 4],
    },
    {
        "name": "Bob",
        "type": "Spam",
        "pos1": [2, 3],
        "pos2": [4, 5],
    },
], axis_order=[1, 0])


tests["test_warn_eclipsed"] = ZoneManager([
    {
        "name": "Bob",
        "type": "Spam",
        "pos1": [1, 1],
        "pos2": [5, 5],
    },
    {
        "name": "Alice",
        "type": "Eggs",
        "pos1": [2, 2],
        "pos2": [4, 4],
    },
], axis_order=[1, 0])


test = tests["region_2"]

zones_start = len(test)

print("-"*120)

for i in range(len(test)):
    zone = test[i]
    print("{:>3} {:>25} {:>3} {:>14} {:<20} {:<20}".format(repr(i), zone.name, repr(zone.original_id), zone.type, repr(zone.pos1.list), repr(zone.pos2.list)))

print("-"*120)

for zone in test.overlaping_zones():
    print("{:>55} {:>3} {:>14} {:<20} {:<20}".format(zone.name, repr(zone.original_id), zone.type, repr(zone.pos1.list), repr(zone.pos2.list)))

print("="*120)

print("Removing overlaps...")
test.remove_overlaps()

print("="*120)

zones_end = len(test)

print("-"*120)

for i in range(len(test)):
    zone = test[i]
    print("{:>3} {:>25} {:>3} {:>14} {:<20} {:<20}".format(repr(i), zone.name, repr(zone.original_id), zone.type, repr(zone.pos1.list), repr(zone.pos2.list)))

print("-"*120)
print("Done.")

print("Zones at start: {}".format(zones_start))
print("Zones at end:   {}".format(zones_end))

print("="*120)
print("Look out for that tree!")

tree = test.get_tree()
tree.show_tree()

print("-"*120)
print("Max depth: {}".format(tree.max_depth()))

