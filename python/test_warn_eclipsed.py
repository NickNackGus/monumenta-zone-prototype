#!/usr/bin/env python3

# For interactive shell
import readline
import code

from lib.pos import Pos
from lib.zone import Zone
from lib.zone_manager import ZoneManager

test = ZoneManager([
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
test.optimize()

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

