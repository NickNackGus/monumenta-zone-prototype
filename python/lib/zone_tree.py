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

        # This is a parent node; this method handles all attributes required for it.
        self._init_parent_node(zones)

    def _init_parent_node(self, zones, debug=False):
        """Determine which way to split the undivided zones.

        Best split results having the lowest maximum of
        the less, mid, and more groups.
        """
        if len(zones) < 2:
            raise IndexError("Cannot split fewer than two zones!")

        num_axes = len(zones[0].max_corner)

        # priority, axis, pivot, less, mid, more
        # Default is an impossibly worst case scenario so it will never be chosen.
        worst_case = { # Use a stuct or dumb class probably
            "priority": len(zones) + 1,
            "axis": 0,

            "pivot": 0,
            "pivot_min": 0,
            "pivot_max": 0,

            "less": [],
            "mid": list(zones),
            "more": [],
        }
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
                for pivot in (pivot_zone.min_corner[axis], pivot_zone.true_max_corner[axis]):
                    less = []
                    pivot_min = pivot
                    mid = []
                    pivot_max = pivot
                    more = []

                    for zone in zones:
                        if pivot >= zone.true_max_corner[axis]:
                            less.append(zone)
                        elif pivot >= zone.min_corner[axis]:
                            pivot_min = min(pivot_min, zone.min_corner[axis])
                            pivot_max = max(pivot_max, zone.true_max_corner[axis])
                            mid.append(zone)
                        else:
                            more.append(zone)

                    test_split = {
                        "priority": max(len(less), len(mid), len(more)),
                        "axis": axis,

                        "pivot": pivot,
                        "pivot_min": pivot_min,
                        "pivot_max": pivot_max,

                        "less": less,
                        "mid": mid,
                        "more": more,
                    }
                    if debug:
                        print("- {!r}".format(test_split))

                    if test_split["priority"] >= best_split["priority"]:
                        continue

                    best_split = test_split
                    if debug:
                        print("  - New best!")

        if worst_case["priority"] == best_split["priority"]:
            # This shouldn't ever happen! Debug mode on if it wasn't on before!
            if not debug:
                self._init_parent_node(zones, debug=True)
            else:
                # This could be an assert instead, but I don't have that documentation marked offline and I have no data half my commute.
                raise AssertionError("Could not find a solution.")
        else:
            # Ok good, this is the answer we want. Copy values to self.
            self._axis = best_split["axis"]

            self._pivot = best_split["pivot"]
            self._pivot_min = best_split["pivot_min"]
            self._pivot_max = best_split["pivot_max"]

            self._less = ZoneTree(best_split["less"])
            self._mid = ZoneTree(best_split["mid"])
            self._more = ZoneTree(best_split["more"])
            return

    def get_zone(self, pos):
        """Get the zone a position is in."""
        comparisons = 1
        if self.is_empty:
            return {"comparisons": 1, "zone": None}

        elif self.is_parent_node:
            comparisons += 1 + 1
            result = None
            if pos[self._axis] > self._pivot:
                result = self._more.get_zone(pos)
                result["comparisons"] += comparisons + 1
                comparisons = result["comparisons"]
                if result["zone"] is not None:
                    return result
            else:
                result = self._less.get_zone(pos)
                result["comparisons"] += comparisons + 1
                comparisons = result["comparisons"]
                if result["zone"] is not None:
                    return result

            # The result could be in the middle tree; search there if possible, and give up if it's not there.
            comparisons += 2
            if self._pivot_min <= pos[self._axis] and pos[self._axis] < self._pivot_max:
                result = self._mid.get_zone(pos)
                result["comparisons"] += comparisons
                comparisons = result["comparisons"]
                # If we find no zone, we're out of places to look - that's the result.
                # Ancestor nodes may find something in their mid trees, though.
                return result

            return result

        else: # Leaf node
            comparisons += 1 + 2*len(pos)
            if self.here.within(pos):
                return {"comparisons": comparisons, "zone": self.here}
            else:
                return {"comparisons": comparisons, "zone": None}

########################################################################################################################
# Only needed for debug and statistics:

    def __iter__(self):
        if self.is_empty:
            raise StopIteration

        elif self.is_parent_node:
            for zone in self._less:
                yield zone
            for zone in self._mid:
                yield zone
            for zone in self._more:
                yield zone

        else: # Leaf node
            yield self.here

    def __len__(self):
        if self.is_empty:
            return 0

        elif self.is_parent_node:
            return len(self._less) + len(self._mid) + len(self._more)

        else: # Leaf node
            return 1

    def max_depth(self):
        """Debug info only."""
        if self.is_empty:
            return 0

        elif self.is_parent_node:
            return 1 + max(
                self._less.max_depth(),
                self._mid.max_depth(),
                self._more.max_depth()
            )

        else: # Leaf node
            return 1

    def all_leaf_depths(self):
        """Debug info only."""
        if self.is_empty:
            return []

        elif self.is_parent_node:
            return [leaf_depth + 1 for leaf_depth in self._less.all_leaf_depths() + self._mid.all_leaf_depths() + self._more.all_leaf_depths()]

        else: # Leaf node
            return [1]

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

        if self.is_empty:
            print(prefix + "╴" + "<Tree is empty>")

        elif self.is_parent_node:
            print(prefix + "┬╴axis={!r}, pivot={!r}, mid_min={!r}, mid_max={!r}".format(self._axis, self._pivot, self._pivot_min, self._pivot_max))

            if header:
                prefix = " " * len(header)

            prefix = prefix.replace("─", " ")
            prefix = prefix.replace("├", "│")
            prefix = prefix.replace("└", " ")

            self._less.show_tree(None, prefix + "├─")
            self._mid.show_tree(None,  prefix + "├─")
            self._more.show_tree(None, prefix + "└─")

        else: # Leaf node
            print(prefix + "╴" + repr(self.here))

