#!/usr/bin/env python3

# For interactive shell
import readline
import code

import json
from lib.pos import Pos
from lib.zone import Zone
from lib.zone_manager import ZoneManager

tests = {}


with open("../config/region_2.json", "r") as fp:
    region_2_prop = json.load(fp)
    fp.close()

test = ZoneManager(region_2_prop["locationBounds"])

test.remove_overlaps()
print("Look out for that tree!")

tree = test.get_tree()
tree.show_tree()

print("-"*120)
print("Max depth: {}".format(tree.max_depth()))

