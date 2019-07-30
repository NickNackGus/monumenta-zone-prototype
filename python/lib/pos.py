#!/usr/bin/env python3

from copy import deepcopy

class Pos(object):
    def __init__(self, other):
        if isinstance(other, type(self)):
            self.list = deepcopy(other.list)
        elif isinstance(other, str):
            self.list = []
            for coord_str in other.split():
                self.list.append(int(coord_str))
        elif isinstance(other, tuple):
            self.list = list(other)
        elif isinstance(other, list):
            self.list = list(other)
        else:
            raise TypeError("Unexpected type {}: {}".format(type(other), other))


    def __len__(self):
        return len(self.list)

    def __getitem__(self, key):
        return self.list[key]

    def __setitem__(self, key, value):
        if not isinstance(value, float) and not isinstance(value, int):
            raise TypeError("Coordinate must be numeric")
        self.list[key] = value


    def __eq__(self, other):
        return self.list == other.list

    def __ne__(self, other):
        return self.list != other.list


    def __iadd__(self, other):
        for axis in range(len(self)):
            self[axis] += other[axis]
        return self

    def __add__(self, other):
        result = Pos(self)
        result += Pos(other)
        return result

    def __radd__(self, other):
        result = Pos(other)
        result += Pos(self)
        return result


    def __isub__(self, other):
        for axis in range(len(self)):
            self[axis] -= other[axis]
        return self

    def __sub__(self, other):
        result = Pos(self)
        result -= Pos(other)
        return result

    def __rsub__(self, other):
        result = Pos(other)
        result -= Pos(self)
        for axis in range(len(result)):
            result[axis] *= -1
        return result


    def min_corner(self, others):
        result = deepcopy(self.list)
        if isinstance(others, type(self)):
            others = [others]
        for other in others:
            for i in range(len(result)):
                result[i] = min(result[i], other.list[i])
        return Pos(result)

    def max_corner(self, others):
        result = deepcopy(self.list)
        if isinstance(others, type(self)):
            others = [others]
        for other in others:
            for i in range(len(result)):
                result[i] = max(result[i], other.list[i])
        return Pos(result)


    def __hash__(self):
        return hash(repr(self))

    def __repr__(self):
        return "Pos({})".format(self.list)

