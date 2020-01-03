#!/usr/bin/env python3

from lib.zone.zone import Zone
from lib.zone_tree.zone_tree_base import ZoneTreeBase

class ZoneTreeLeaf(ZoneTreeBase):
    """A tree of zones for fast search."""
    def __init__(self, zones=[]):
        """Create a zone tree. Zone fragments must not overlap to load."""
        self.here = zones[0]

    def get_zone(self, pos):
        """Get the zone a position is in."""
        if self.here.within(pos):
            return self.here.parent
        else:
            return None

########################################################################################################################
# Only needed for debug and statistics:

    def __iter__(self):
        yield self.here

    def __len__(self):
        return 1

    def max_depth(self):
        """Debug info only."""
        return 1

    def all_leaf_depths(self):
        """Debug info only."""
        return [1]

    def total_leaf_depth(self):
        """Debug info only."""
        return 1

    def average_depth(self):
        """Debug info only."""
        return 1

    def show_tree(self, header="─", prefix=""):
        """Print the tree structure to stdout for debugging."""
        if header:
            prefix = header

        print(prefix + "╴" + repr(self.here))

