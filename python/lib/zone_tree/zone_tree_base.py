#!/usr/bin/env python3

from lib.zone.zone import Zone
# These are imported later because of Python's strange circular dependency issues; Java does not require this.
#from lib.zone_tree.zone_tree_empty import ZoneTreeEmpty
#from lib.zone_tree.zone_tree_leaf import ZoneTreeLeaf
#from lib.zone_tree.zone_tree_parent import ZoneTreeParent

class ZoneTreeBase(Zone):
    """The base class of a tree of zones for fast search."""
    @staticmethod
    def CreateZoneTree(zones=[]):
        if len(zones) == 0:
            from lib.zone_tree.zone_tree_empty import ZoneTreeEmpty
            return ZoneTreeEmpty()
        elif len(zones) == 1:
            from lib.zone_tree.zone_tree_leaf import ZoneTreeLeaf
            return ZoneTreeLeaf(zones)
        else:
            from lib.zone_tree.zone_tree_parent import ZoneTreeParent
            return ZoneTreeParent(zones)

    def __init__(self, zones=[]):
        """Create a zone tree. Zone fragments must not overlap to load."""
        pass

    def get_zone(self, pos):
        """Get the zone a position is in."""
        pass

########################################################################################################################
# Only needed for debug and statistics:

    def __iter__(self):
        pass

    def __len__(self):
        pass

    def max_depth(self):
        """Debug info only."""
        pass

    def all_leaf_depths(self):
        """Debug info only."""
        pass

    def total_leaf_depth(self):
        """Debug info only."""
        pass

    def average_depth(self):
        """Debug info only."""
        pass

    def show_tree(self, header="─", prefix=""):
        """Print the tree structure to stdout for debugging."""
        pass

