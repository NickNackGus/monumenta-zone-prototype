#!/usr/bin/env python3

from copy import deepcopy
from lib.pos import Pos

class Zone(object):
    """A zone where non-standard behavior occurs.

    pos2 is being rewritten to be exclusive, not inclusive.
    """
    def __init__(self, other=None, name=None, ztype=None, equipment_damage=None, pos=None, size=None, parents=[], axis_order=None, original_id=None):
        self.original_id = None

        if isinstance(other, type(self)):
            self._init_from_zone(other)

        elif isinstance(other, dict):
            # This uses an inclusive pos2 for compatibility
            self._init_from_config(other, axis_order, original_id)

        elif other is None:
            self._init_from_values(name, ztype, equipment_damage, pos, size, parents, axis_order, original_id)

        else:
            raise TypeError("Expected Zone to be initialized with a dict or another Zone")

        if self.original_id is None:
            self.original_id = original_id

        self.children = []
        for parent in self.parents:
            parent.children.append(self)

    def _init_from_zone(self, other):
        self.name = other.name
        self.type = other.type
        self.equipment_damage = other.equipment_damage
        self._pos = deepcopy(other._pos)
        self._size = deepcopy(other._size)
        self.parents = [other]
        self.axis_order = deepcopy(other.axis_order)
        self.original_id = other.original_id

    def _init_from_config(self, other, axis_order, original_id):
        self.name = other["name"]
        self.type = other["type"]
        self.equipment_damage = other.get("equipmentDamage", None)

        a = Pos(other["pos1"])
        b = Pos(other["pos2"])

        self._pos = a.min_corner(b)
        self._size = a.max_corner(b) + Pos([1]*len(self._pos)) - self._pos

        self.parents = []

        # Order to process axes, such as [0, 2, 1]
        if axis_order is None:
            axis_order = list(range(len(self._pos)))
        self.axis_order = axis_order

        self.original_id = original_id

    def _init_from_values(self, name, ztype, equipment_damage, pos, size, parents, axis_order, original_id):
        self.name = name
        self.type = ztype
        self.equipment_damage = equipment_damage
        self._pos = Pos(pos)
        self._size = Pos(size)
        self.parents = parents

        # Order to process axes, such as [0, 2, 1]
        if axis_order is None:
            axis_order = list(range(len(self._pos)))
        self.axis_order = axis_order

        self.original_id = original_id

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
        m = self.max_corner

        for i in range(len(pos)):
            if l[i] > pos[i]:
                return False
            if pos[i] >= m[i]:
                return False
        return True

    def overlaping_zones(self, other):
        if not isinstance(other, Zone):
            raise TypeError("Expected other to be type Zone.")

        self_min, self_max = self.min_corner, self.max_corner
        other_min, other_max = other.min_corner, other.max_corner

        for axis in self.axis_order:
            if axis > len(other_max):
                continue

            if other_max[axis] <= self_min[axis]:
                return None

            if self_max[axis] <= other_min[axis]:
                return None

        result_min = self_min.max_corner(other_min)
        result_max = self_max.min_corner(other_max)

        result_size = result_max - result_min + Pos([1]*len(self._pos))

        return Zone(
            name="{} X {}".format(self.name, other.name),
            ztype=self.type,
            pos=result_min,
            size=result_size,
            parents=[self, other]
        )

    def split_by_overlap(self, overlap):
        # overlap is an area that overlaps and doesn't extend beyond this zone.
        if not isinstance(overlap, Zone):
            raise TypeError("Expected overlap to be type Zone.")

        work = Zone(self)
        work.parents.append(overlap)

        other_min = overlap.min_corner
        other_max = overlap.max_corner + Pos([1]*len(other_min))

        result = []

        for axis in self.axis_order:
            if axis > len(other_max):
                continue

            lower, work = work.split_axis(other_min, axis)
            work.parents = work.parents[0]
            if lower:
                result.append(lower)

            work, upper = work.split_axis(other_max, axis)
            work.parents = work.parents[0]
            if upper:
                result.append(upper)

        if not work:
            print("{} is completely eclipsed by {}!".format(self, overlap))

        return result

    def split_axis(self, pos, axis):
        """Returns (lower_zone, upper_zone) for this split along some axis.

        upper_inclusive is True if pos is in upper, False if pos is in Lower
        Either zone may have a size of 0.
        """
        lower = Zone(self)
        lower._size[axis] = pos[axis] - lower._pos[axis]

        upper = Zone(self)
        upper._size[axis] -= lower._size[axis]
        upper._pos[axis] += lower._size[axis]

        return (lower, upper)

    def __repr__(self):
        if self: # None-zero size
            if self.equipment_damage is None:
                return (
                    'Zone({'
                    + '"name": {!r}, "type": {!r}, "pos1": {!r}, "pos2": {!r}'.format(self.name, self.type, self.pos1.list, self.pos2.list)
                    + '}'
                    + ', axis_order={!r}, original_id={!r})'.format(self.axis_order, self.original_id)
                )

            else:
                return (
                    'Zone({'
                    + '"name": {!r}, "type": {!r}, "equipment_damage": {!r}, "pos1": {!r}, "pos2": {!r}'.format(self.name, self.type, self.equipment_damage, self.pos1.list, self.pos2.list)
                    + '}'
                    + ', axis_order={!r}, original_id={!r})'.format(self.axis_order, self.original_id)
                )

        else:
            return "Zone(name={!r}, ztype={!r}, equipment_damage={!r}, pos={!r}, size={!r})".format(self.name, self.type, self.equipment_damage, self._pos, self._size)

