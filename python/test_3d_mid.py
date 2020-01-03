#!/usr/bin/env python3

from lib.pos import Pos
from lib.zone_manager import ZoneManager

test = ZoneManager([
    {
        "name": "Alice",
        "type": "Eggs",
        "pos1": [2, 2, 2],
        "pos2": [2, 2, 2],
    },
    {
        "name": "Bob",
        "type": "Spam",
        "pos1": [1, 1, 1],
        "pos2": [3, 3, 3],
    },
])

print("-"*120)

for i, zone in enumerate(test):
    print("{:>3} {}".format(repr(i), repr(zone)))

print("-"*120)

for zone in test.overlaping_zones():
    print(repr(zone))

print("="*120)

tree = test.tree

print("-"*120)
print("Ave depth:  {:04.2f}".format(tree.average_depth()))
print("Max depth:  {}".format(tree.max_depth()))
print("Leaf nodes: {}".format(len(tree)))

print("="*120)
print("Look out for that tree!")
tree.show_tree()

