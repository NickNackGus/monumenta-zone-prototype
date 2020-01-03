#!/usr/bin/env python3

from copy import deepcopy
from lib.pos import Pos

class ZoneBase(object):
    """A base zone where non-standard behavior occurs.

    May be the entire area, or just a fragment.
    Does not contain zone properties or fragments.

    pos2 is being rewritten to be exclusive, not inclusive.
    """
    def __init__(self, other=None, pos=None, size=None):
        if isinstance(other, ZoneBase):
            self._init_from_zone(other)

        elif isinstance(other, dict):
            # This uses an inclusive pos2 for compatibility
            self._init_from_config(other)

        elif other is None:
            self._init_from_values(pos, size)

        else:
            raise TypeError("Expected ZoneBase to be initialized with a dict or another ZoneBase")

    def _init_from_zone(self, other):
        self._pos = deepcopy(other._pos)
        self._size = deepcopy(other._size)

    def _init_from_config(self, other):
        a = Pos(other["pos1"])
        b = Pos(other["pos2"])

        self._pos = a.min_corner(b)
        self._size = a.max_corner(b) + Pos([1]*len(self._pos)) - self._pos

    def _init_from_values(self, pos, size):
        self._pos = Pos(pos)
        self._size = Pos(size)

    @property
    def pos1(self):
        return self._pos

    @property
    def pos2(self):
        return self._pos + self._size - Pos([1]*len(self._pos))

    def __bool__(self):
        return self.volume() != 0

    @property
    def min_corner(self):
        return self.pos1

    @property
    def max_corner(self):
        return self.pos2

    @property
    def true_max_corner(self):
        return self.pos1 + self.size()

    @min_corner.setter
    def min_corner(self, other):
        new_pos1 = Pos(other)
        self._size += self._pos - new_pos1
        self._pos = new_pos1

    @max_corner.setter
    def max_corner(self, other):
        new_max = Pos(other)
        old_max = self.pos2
        self._size += new_max - old_max

    @true_max_corner.setter
    def true_max_corner(self, other):
        new_max = Pos(other)
        old_max = self.true_max_corner
        self._size += new_max - old_max

    def size(self):
        return list(self._size.list)

    def volume(self):
        size = self.size()
        result = 1

        for axis_size in size:
            result *= axis_size

        return result

    def within(self, pos):
        if self.volume() == 0:
            return False

        l = self.min_corner
        m = self.true_max_corner

        for i in range(len(pos)):
            if pos[i] < l[i]:
                return False
            if m[i] <= pos[i]:
                return False
        return True

    def overlaping_zone(self, other):
        if not isinstance(other, ZoneBase):
            raise TypeError("Expected other to be type ZoneBase.")

        self_min, self_max = self.min_corner, self.max_corner
        other_min, other_max = other.min_corner, other.max_corner

        for axis in range(len(self._pos)):
            if other_max[axis] < self_min[axis]:
                return None

            if self_max[axis] < other_min[axis]:
                return None

        result_min = self_min.max_corner(other_min)
        result_max = self_max.min_corner(other_max)

        result_size = result_max - result_min + Pos([1]*len(self._pos))

        result = ZoneBase(
            pos=result_min,
            size=result_size
        )

        if not result:
            return None

        return result

########################################################################################################################
# Only needed for debug and statistics:

    def __repr__(self):
        return "ZoneBase(pos={!r}, size={!r})".format(self._pos, self._size)
