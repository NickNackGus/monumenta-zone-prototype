#!/usr/bin/env python3

from copy import deepcopy
from lib.pos import Pos
from lib.zone.zone_base import ZoneBase
# Circular dependency workaround for Python; can be a normal import for Java
import lib.zone.zone as zone

class ZoneFragment(ZoneBase):
    """A zone fragment where non-standard behavior occurs.

    pos2 is being rewritten to be exclusive, not inclusive.
    """
    def __init__(self, other, axis_order=None):
        super().__init__(other)

        if isinstance(other, ZoneFragment):
            self.parent = other.parent
            self.axis_order = deepcopy(other.axis_order)

        elif isinstance(other, zone.Zone):
            self.parent = other
            self.axis_order = axis_order

        else:
            raise TypeError("Expected ZoneFragment to be initialized with a Zone or another ZoneFragment")

    def split_axis(self, pos, axis):
        """Returns (lower_zone, upper_zone) for this split along some axis.

        Either zone may have a size of 0.
        """
        lower = ZoneFragment(self)
        lower._size[axis] = pos[axis] - lower._pos[axis]

        upper = ZoneFragment(self)
        upper._size[axis] -= lower._size[axis]
        upper._pos[axis] += lower._size[axis]

        return (lower, upper)

    def split_by_overlap(self, overlap):
        """Returns a list of fragments of this zone, split by an overlapping zone."""
        # overlap is a ZoneBase that overlaps and doesn't extend beyond this ZoneFragment.
        if not isinstance(overlap, ZoneBase):
            raise TypeError("Expected overlap to be type ZoneBase.")

        center_zone = ZoneFragment(self)

        other_min = overlap.min_corner
        other_max = overlap.max_corner + Pos([1]*len(other_min))

        result = []

        for axis in self.axis_order:
            if axis > len(other_max):
                # Skip axis if they don't apply
                continue

            work_zones = result
            result = []

            for work_zone in work_zones:
                # Add zones split from existing split zones
                lower, work_zone = work_zone.split_axis(other_min, axis)
                work_zone, upper = work_zone.split_axis(other_max, axis)

                if lower:
                    result.append(lower)
                if work_zone:
                    result.append(work_zone)
                if upper:
                    result.append(upper)

            # Add zones split from center, but not the center (overlap) itself
            lower, center_zone = center_zone.split_axis(other_min, axis)
            center_zone, upper = center_zone.split_axis(other_max, axis)

            if lower:
                result.append(lower)
            if upper:
                result.append(upper)

        return result

    def merge(self, other):
        """Merge two ZoneFragments without changing their combined size/shape.

        Returns the merged ZoneFragment or None.
        """
        a_min = self.min_corner
        b_min = other.min_corner
        a_size = self.size()
        b_size = other.size()

        # Confirm the ZoneFragments can be merged without extending outside their bounds
        different_axis = -1
        for axis in range(len(a_min)):
            if (
                a_min[axis] == b_min[axis]
                and a_size[axis] == b_size[axis]
            ):
                # This axis matches, all good so far
                continue

            if different_axis == -1:
                # First different axis we've found
                different_axis = axis
            else:
                # Second different axis; no merging this time
                return None

        if different_axis == -1:
            # Same zone
            return ZoneFragment(self)
        axis = different_axis

        # Confirm the two zones are touching
        if (
            a_min[axis] + a_size[axis] != b_min[axis] and
            b_min[axis] + b_size[axis] != a_min[axis]
        ):
            # They are not touching.
            return None

        # Merging is possible, go for it.
        result = ZoneFragment(self)
        min_corner = result.min_corner
        max_corner = result.max_corner
        min_corner[axis] = min(self.min_corner[axis], other.min_corner[axis])
        max_corner[axis] = max(self.max_corner[axis], other.max_corner[axis])
        result.min_corner = min_corner
        result.max_corner = max_corner
        return result

########################################################################################################################
# Only needed for debug and statistics:

    def __repr__(self):
        return "ZoneFragment(parent={!r}, pos={!r}, size={!r}, axis_order={!r})".format(self.parent, self._pos, self._size, self.axis_order)

