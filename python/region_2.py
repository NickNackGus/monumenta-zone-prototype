#!/usr/bin/env python3

# For interactive shell
import readline
import code

import json
from lib.pos import Pos
from lib.zone import Zone
from lib.zone_manager import ZoneManager

with open("../config/region_2.json", "r") as fp:
    region_2_prop = json.load(fp)
    fp.close()

test = ZoneManager(region_2_prop["locationBounds"])

test.remove_overlaps()
test.optimize()

tree = test.get_tree()

print("-"*120)
print("Max depth:  {}".format(tree.max_depth()))
print("Leaf nodes: {}".format(len(tree)))

i = 1
merged = 1
while merged > 0:
    print("="*120)
    print("Optimizing  {}...".format(i))

    merged = tree.optimize()
    tree.rebalance()

    print("Merged:     {}".format(merged))
    print("Max depth:  {}".format(tree.max_depth()))
    print("Leaf nodes: {}".format(len(tree)))

    i += 1

print("="*120)
print("Look out for that tree!")
tree.show_tree()

print("-"*120)
print("Golden block's zone is:")
print("{!r}".format(tree.get_zone(Pos("-1441 2 -1441"))))

