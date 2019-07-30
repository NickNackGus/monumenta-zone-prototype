#!/usr/bin/env python3

# For interactive shell
import readline
import code

from copy import deepcopy
from lib.zone import Zone

class ZoneTree(Zone):
    """A tree of zones for fast search.

    Treat as immutable.
    """
    def __init__(self, zones=[]):
        """A node of the zone tree. Zones must not overlap to load."""
        # The number of nodes in this tree
        self._len = len(zones)

        # This is only set for leaf nodes (len(self) == 1)
        self.here = None

        # Which axis are we checking, and by what coordinate do we pivot?
        self._axis = 0
        self._pivot = None

        # Next node up/here/down on an axis
        self._less = None # Includes overlapping areas
        self._more = None

        if len(zones) == 0:
            return

        elif len(zones) == 1:
            self.here = zones[0]
            return

        else:
            self._axis, self._pivot = self.get_best_split(zones)

            less = []
            more = []

            for zone in zones:
                if self._pivot >= zone.max_corner[self._axis]:
                    more.append(zone)
                else:
                    less.append(zone)

            self._less = ZoneTree(less)
            self._more = ZoneTree(more)

            return

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
            print("Finding best split...")
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
            self.get_best_split(zones, debug=True)
        else:
            return best_split[1], best_split[2]

    def __len__(self):
        return self._len

    def get_zone(self, pos):
        """Get the zone a position is in."""
        if len(self) == 0:
            return None

        elif len(self) == 1:
            if self.here.within(pos):
                return self.here
            else:
                return None

        elif pos[self._axis] >= self._pivot:
            return self._more.get_zone(pos)

        else:
            return self._less.get_zone(pos)

    def max_depth(self):
        if len(self) == 0:
            # Undefined
            return -1

        elif len(self) == 1:
            return 1

        else:
            return 1 + max(
                self._less.max_depth(),
                self._more.max_depth()
            )

    def show_tree(self, header="─", prefix=""):
        """Print the tree structure to stdout for debugging."""
        if header:
            prefix = header

        if len(self) == 0:
            print(prefix + "╴" + "<Tree is empty>")

        elif len(self) == 1:
            print(prefix + "╴" + repr(self.here))

        else:
            print(prefix + "┬╴axis={!r}, pivot={!r}".format(self._axis, self._pivot))

            if header:
                prefix = " " * len(header)

            prefix = prefix.replace("─", " ")
            prefix = prefix.replace("├", "│")
            prefix = prefix.replace("└", " ")

            self._less.show_tree(None, prefix + "├─")
            self._more.show_tree(None, prefix + "└─")

