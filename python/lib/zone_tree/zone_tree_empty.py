#!/usr/bin/env python3

from lib.zone.zone import Zone
from lib.zone_tree.zone_tree_base import ZoneTreeBase

class ZoneTreeEmpty(ZoneTreeBase):
    """A tree of zones for fast search."""
    def __init__(self, zones=[]):
        """Create a zone tree. Zone fragments must not overlap to load."""

    def get_zone(self, pos):
        """Get the zone a position is in."""
        return None

########################################################################################################################
# Only needed for debug and statistics:

    def __iter__(self):
        raise StopIteration

    def __len__(self):
        return 0

    def max_depth(self):
        """Debug info only."""
        return 0

    def all_leaf_depths(self):
        """Debug info only."""
        return []

    def total_leaf_depth(self):
        """Debug info only."""
        return 0

    def average_depth(self):
        """Debug info only."""
        return 0

    def show_tree(self, header="─", prefix=""):
        """Print the tree structure to stdout for debugging."""
        if header:
            prefix = header

        print(prefix + "╴" + "<Tree is empty>")

