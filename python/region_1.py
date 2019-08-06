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

test = ZoneManager(region_1_prop["locationBounds"])

test.remove_overlaps()
print("Look out for that tree!")

tree = test.get_tree()
tree.show_tree()

print("-"*120)
print("Max depth:  {}".format(tree.max_depth()))
print("Leaf nodes: {}".format(len(tree)))

print("="*120)
print("Optimizing...")

tree.optimize()

print("-"*120)
print("Max depth:  {}".format(tree.max_depth()))
print("Leaf nodes: {}".format(len(tree)))

