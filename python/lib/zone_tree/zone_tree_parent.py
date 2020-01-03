#!/usr/bin/env python3

from lib.zone.zone import Zone
from lib.zone_tree.zone_tree_base import ZoneTreeBase

class ZoneTreeParent(ZoneTreeBase):
    """A tree of zones for fast search."""
    def __init__(self, zones=[]):
        """Create a zone tree. Zone fragments must not overlap to load.

        Determine which way to split the undivided zones.

        Best split results having the lowest maximum of
        the less, mid, and more groups.
        """
        num_axes = len(zones[0].max_corner)

        # priority, axis, pivot, less, mid, more
        # Default is an impossibly worst case scenario so it will never be chosen.
        worst_case = { # Use a stuct or dumb class probably
            "priority": len(zones) + 1,
            "axis": 0,

            "pivot": 0,
            "mid_min": 0,
            "mid_max": 0,

            "less": [],
            "mid": list(zones),
            "more": [],
        }
        best_split = worst_case

        for pivot_zone in zones:
            for axis in range(num_axes):
                for pivot in (pivot_zone.min_corner[axis], pivot_zone.true_max_corner[axis]):
                    less = []
                    mid_min = pivot
                    mid = []
                    mid_max = pivot
                    more = []

                    for zone in zones:
                        if pivot >= zone.true_max_corner[axis]:
                            less.append(zone)
                        elif pivot >= zone.min_corner[axis]:
                            mid_min = min(mid_min, zone.min_corner[axis])
                            mid_max = max(mid_max, zone.true_max_corner[axis])
                            mid.append(zone)
                        else:
                            more.append(zone)

                    test_split = {
                        "priority": max(len(less), len(mid), len(more)),
                        "axis": axis,

                        "pivot": pivot,
                        "mid_min": mid_min,
                        "mid_max": mid_max,

                        "less": less,
                        "mid": mid,
                        "more": more,
                    }

                    if test_split["priority"] >= best_split["priority"]:
                        continue

                    best_split = test_split

        # Ok good, this is the answer we want. Copy values to self.
        self._axis = best_split["axis"]

        self._pivot = best_split["pivot"]
        self._mid_min = best_split["mid_min"]
        self._mid_max = best_split["mid_max"]

        self._less = ZoneTreeBase.CreateZoneTree(best_split["less"])
        self._mid = ZoneTreeBase.CreateZoneTree(best_split["mid"])
        self._more = ZoneTreeBase.CreateZoneTree(best_split["more"])
        return

    def get_zone(self, pos):
        """Get the zone a position is in."""
        result = None
        if pos[self._axis] > self._pivot:
            result = self._more.get_zone(pos)
            if result is not None:
                return result
        else:
            result = self._less.get_zone(pos)
            if result is not None:
                return result

        # The result could be in the middle tree; search there if possible, and give up if it's not there.
        if self._mid_min <= pos[self._axis] and pos[self._axis] < self._mid_max:
            result = self._mid.get_zone(pos)
            # If we find no zone, we're out of places to look - that's the result.
            # Ancestor nodes may find something in their mid trees, though.
            return result

        return result

########################################################################################################################
# Only needed for debug and statistics:

    def __iter__(self):
        for zone in self._less:
            yield zone
        for zone in self._mid:
            yield zone
        for zone in self._more:
            yield zone

    def __len__(self):
        return len(self._less) + len(self._mid) + len(self._more)

    def max_depth(self):
        """Debug info only."""
        return 1 + max(
            self._less.max_depth(),
            self._mid.max_depth(),
            self._more.max_depth()
        )

    def all_leaf_depths(self):
        """Debug info only."""
        return [leaf_depth + 1 for leaf_depth in self._less.all_leaf_depths() + self._mid.all_leaf_depths() + self._more.all_leaf_depths()]

    def total_leaf_depth(self):
        """Debug info only."""
        result = 0
        for leaf_depth in self.all_leaf_depths():
            result += leaf_depth
        return result

    def average_depth(self):
        """Debug info only."""
        return self.total_leaf_depth() / len(self)

    def show_tree(self, header="─", prefix=""):
        """Print the tree structure to stdout for debugging."""
        if header:
            prefix = header

        print(prefix + "┬╴axis={!r}, pivot={!r}, mid_min={!r}, mid_max={!r}".format(self._axis, self._pivot, self._mid_min, self._mid_max))

        if header:
            prefix = " " * len(header)

        prefix = prefix.replace("─", " ")
        prefix = prefix.replace("├", "│")
        prefix = prefix.replace("└", " ")

        self._less.show_tree(None, prefix + "├─")
        self._mid.show_tree(None,  prefix + "├─")
        self._more.show_tree(None, prefix + "└─")

