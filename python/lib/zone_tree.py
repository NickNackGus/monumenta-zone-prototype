#!/usr/bin/env python3

# For interactive shell
import readline
import code

from copy import deepcopy
from lib.zone import Zone

class ZoneTree(Zone):
    """A tree of zones for fast search."""
    def __init__(self, zones=[]):
        """Create a zone tree. Zones must not overlap to load."""
        self._init(zones)

    def _init(self, zones):
        """Load a list of zones. Reused by the rebalance method."""
        # True if this is an empty tree
        self.is_empty = False
        if len(zones) == 0:
            self.is_empty = True
            return

        # True if this node is a parent node, False if it is one zone
        self.is_parent_node = True
        if len(zones) == 1:
            self.is_parent_node = False

            # This is only set for leaf nodes
            self.here = zones[0]
            return

        #######################################################################
        # Everything past here applies only to parent nodes

        # Which axis are we checking, and by what coordinate do we pivot?
        self._axis, self._pivot = self.get_best_split(zones)

        less = []
        more = []
        for zone in zones:
            if self._pivot >= zone.max_corner[self._axis]:
                more.append(zone)
            else:
                less.append(zone)

        # Next node up/here/down on an axis
        self._less = ZoneTree(less) # Includes overlapping areas
        self._more = ZoneTree(more)

    def rebalance(self):
        """Rebalance the nodes of the tree."""
        zones = list(self)
        self.uninit()
        self._init(zones)

    def uninit(self):
        """Uninitialize this node, deleting child nodes in the process."""
        if self.is_empty:
            self.is_empty = False

        elif self.is_parent_node:
            self._less.uninit()
            self._more.uninit()

            del self._less
            del self._more

            self.is_parent_node = False

        else: # Leaf node
            del self.here

    def get_zone(self, pos):
        """Get the zone a position is in."""
        comparisons = 0
        if self.is_empty:
            comparisons += 1
            return {"comparisons": 1, "zone": None}

        elif self.is_parent_node:
            comparisons += 1 + 1
            if pos[self._axis] >= self._pivot:
                comparisons += 1
                result = self._more.get_zone(pos)
                result["comparisons"] += comparisons
                return result
            else:
                comparisons += 1
                result = self._less.get_zone(pos)
                result["comparisons"] += comparisons
                return result

        else: # Leaf node
            comparisons += 1 + 1
            if self.here.within(pos):
                comparisons += 2*len(pos)
                return {"comparisons": comparisons, "zone": self.here}
            else:
                comparisons += 2*len(pos)
                return {"comparisons": comparisons, "zone": None}

    def get_best_split(self, zones, debug=False):
        """Determine which way to split the undivided zones.

        Best split results in more and less having an equal number of zones
        on each side, or as close as possible.
        """
        if len(zones) < 2:
            raise IndexError("Cannot split fewer than two zones!")

        num_axes = len(zones[0].max_corner)

        # max(len(less), len(more)), axis, pivot
        # Default is an impossibly worst case scenario so it will never be chosen.
        worst_case = (len(zones), 0, zones[0].max_corner[0])
        best_split = worst_case
        if debug:
            print("="*120)
            print("Finding best split for:")
            for zone in zones:
                print("- {!r}".format(zone))
            print("Worst case:")
            print(worst_case)
            print("-"*120)

        for pivot_zone in zones:
            for axis in range(num_axes):
                pivot = pivot_zone.max_corner[axis]

                less = 0
                more = 0

                for zone in zones:
                    if pivot >= zone.max_corner[axis]:
                        more += 1
                    else:
                        less += 1

                test_split = (max(less, more), axis, pivot)
                if debug:
                    print("- {!r}".format(test_split))

                if test_split[0] >= best_split[0]:
                    continue

                best_split = test_split
                if debug:
                    print("  - New best!")

        if worst_case[0] == best_split[0]:
            if not debug:
                self.get_best_split(zones, debug=True)
        else:
            return best_split[1], best_split[2]

    def __iter__(self):
        if self.is_empty:
            raise StopIteration

        elif self.is_parent_node:
            for zone in self._less:
                yield zone
            for zone in self._more:
                yield zone

        else: # Leaf node
            yield self.here

    def __len__(self):
        if self.is_empty:
            return 0

        elif self.is_parent_node:
            return len(self._less) + len(self._more)

        else: # Leaf node
            return 1

    def max_depth(self):
        if self.is_empty:
            return 0

        elif self.is_parent_node:
            return 1 + max(
                self._less.max_depth(),
                self._more.max_depth()
            )

        else: # Leaf node
            return 1

    def optimize(self):
        """Merge nodes where possible.

        This will be replaced by the optimize method in zone_manager if it's better.
        Returns the number of merges that occured.
        """
        merged = 0
        if self.is_empty or not self.is_parent_node:
            return merged

        if self._less.is_parent_node:
            merged += self._less.optimize()
        if self._more.is_parent_node:
            merged += self._more.optimize()

        if self._less.is_parent_node or self._more.is_parent_node:
            return merged

        # Both child nodes are leaf nodes.
        less = self._less.here
        more = self._more.here

        if less.original_id != more.original_id:
            return merged

        merged_zone = less.merge(more)
        if merged_zone is None:
            return merged
        self.here = merged_zone

        # Mark self as a leaf node, not a parent node
        self.is_parent_node = False

        # Delete unneeded attributes
        del self._axis
        del self._pivot
        del self._less
        del self._more

        # This is merged, increment count
        merged += 1

        return merged

    def show_tree(self, header="─", prefix=""):
        """Print the tree structure to stdout for debugging."""
        if header:
            prefix = header

        if self.is_empty:
            print(prefix + "╴" + "<Tree is empty>")

        elif self.is_parent_node:
            print(prefix + "┬╴axis={!r}, pivot={!r}".format(self._axis, self._pivot))

            if header:
                prefix = " " * len(header)

            prefix = prefix.replace("─", " ")
            prefix = prefix.replace("├", "│")
            prefix = prefix.replace("└", " ")

            self._less.show_tree(None, prefix + "├─")
            self._more.show_tree(None, prefix + "└─")

        else: # Leaf node
            print(prefix + "╴" + repr(self.here))

