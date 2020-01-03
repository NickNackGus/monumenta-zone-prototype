#!/usr/bin/env python3

import json
from lib.pos import Pos
from lib.zone_manager import ZoneManager

with open("../config/region_2.json", "r") as fp:
    region_2_prop = json.load(fp)
    fp.close()

test = ZoneManager(region_2_prop["locationBounds"])
tree = test.tree

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

