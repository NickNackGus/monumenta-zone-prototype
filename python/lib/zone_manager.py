#!/usr/bin/env python3

# For interactive shell
import readline
import code

from copy import deepcopy
from lib.pos import Pos
from lib.zone.zone import Zone
from lib.zone_tree.zone_tree_base import ZoneTreeBase

class ZoneManager(object):
    def __init__(self, zones=[], axis_order=[0, 2, 1]):
        # axis_order is the order axes are processed, such as [0, 2, 1]
        self.axis_order = axis_order
        self.zones = []
        for i, zone in enumerate(zones):
            self.zones.append(Zone(zone, axis_order=axis_order, original_id=i))
        self._remove_overlaps()
        self._defragment()

        fragments = []
        for zone in self.zones:
            fragments += zone.fragments
        self.tree = ZoneTreeBase.CreateZoneTree(fragments)

    def __len__(self):
        return len(self.zones)

    def __getitem__(self, key):
        return self.zones[key]

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
        for i, a in enumerate(self.zones):
            for b in self.zones[i+1:]:
                overlap = a.overlaping_zone(b)
                if overlap:
                    yield overlap

    def _remove_overlaps(self):
        for i, outer in enumerate(self.zones):
            for inner in self.zones[i+1:]:
                overlap = outer.overlaping_zone(inner)
                if overlap is not None:
                    inner.split_by_overlap(overlap)
                    if len(inner.fragments) == 0:
                        print("WARNING: TOTAL ECLIPSE of {} by {}!".format(inner, outer))

    def _defragment(self):
        """Merge zone fragments to speed up searches later.

        Must remove overlaps before running, or this is pointless!
        """
        # First zone is never fragmented
        for zone in self.zones[1:]:
            zone.defragment()

    ########################################################################################################################
    # Only needed for debug and statistics:

    def __repr__(self):
        return "ZoneManager({})".format(self.zones)

