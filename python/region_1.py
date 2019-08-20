#!/usr/bin/env python3

# For interactive shell
import readline
import code

import json
from lib.pos import Pos
from lib.zone import Zone
from lib.zone_manager import ZoneManager

with open("../config/region_1.json", "r") as fp:
    region_1_prop = json.load(fp)
    fp.close()

test = ZoneManager(region_1_prop["locationBounds"])

test.remove_overlaps()
test.optimize()

tree = test.get_tree()

print("-"*120)
print("Ave depth:  {:04.2f}".format(tree.average_depth()))
print("Max depth:  {}".format(tree.max_depth()))
print("Leaf nodes: {}".format(len(tree)))

print("="*120)
print("Look out for that tree!")
tree.show_tree()

print("-"*120)
print("Golden block's zone is:")
print("{!r}".format(tree.get_zone(Pos("-1441 2 -1441"))))

