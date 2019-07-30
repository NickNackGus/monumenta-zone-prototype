#!/usr/bin/env python3

# For interactive shell
import readline
import code

from copy import deepcopy
from lib.pos import Pos
from lib.zone import Zone
from lib.zone_tree import ZoneTree

class ZoneManager(object):
    def __init__(self, zones=[], axis_order=[0, 2, 1]):
        # axis_order is the order axes are processed, such as [0, 2, 1]
        self.axis_order = axis_order
        self.zones = []
        for i in range(len(zones)):
            zone = zones[i]
            self.zones.append(Zone(zone, axis_order=axis_order, original_id=i))

    def __len__(self):
        return len(self.zones)

    def __getitem__(self, key):
        return self.zones[key]

    def names(self):
        result = set()
        for zone in self.zones:
            result.add(zone.name)
        return result

    def types(self):
        result = set()
        for zone in self.zones:
            result.add(zone.type)
        return result

    def min_corner(self):
        result = self.zones[0].min_corner()
        for zone in self.zones[1:]:
            result = result.min_corner(zone.min_corner())
        return result

    def max_corner(self):
        result = self.zones[0].max_corner()
        for zone in self.zones[1:]:
            result = result.max_corner(zone.max_corner())
        return result

    def overlaping_zones(self):
        for i in range(len(self.zones)):
            a = self.zones[i]
            for b in self.zones[i+1:]:
                overlap = a.overlaping_zones(b)
                if overlap:
                    yield overlap

    def remove_overlaps(self):
        work = list(self.zones)

        outer_i = 0
        while outer_i < len(work):
            outer = work[outer_i]

            seen = work[:outer_i+1]
            remaining = work[outer_i+1:]
            new_remaining = []

            for inner in remaining:
                overlap = outer.overlaping_zones(inner)

                if overlap:
                    non_overlaps = inner.split_by_overlap(overlap)
                    if len(non_overlaps) == 0:
                        print("WARNING! The zone {} is eclipsed by {}!".format(inner, outer))

                    new_remaining += non_overlaps

                else:
                    new_remaining.append(inner)

            work = seen + new_remaining
            outer_i += 1

        self.zones = work

    def get_tree(self):
        return ZoneTree(self.zones)

    def __repr__(self):
        return "ZoneManager({})".format(self.zones)

