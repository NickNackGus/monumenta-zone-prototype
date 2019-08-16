#!/usr/bin/env python3

# For interactive shell
import readline
import code

from copy import deepcopy
from lib.pos import Pos
from lib.zone import Zone
from lib.zone_tree import ZoneTree

class ZoneManager(object):
    def __init__(self, zones=[], axis_order=[0, 2, 1]):
        # axis_order is the order axes are processed, such as [0, 2, 1]
        self.axis_order = axis_order
        self.zones = []
        self.zone_counts = []
        for i in range(len(zones)):
            zone = zones[i]
            self.zones.append(Zone(zone, axis_order=axis_order, original_id=i))
            self.zone_counts.append(1)

    def __len__(self):
        return len(self.zones)

    def __getitem__(self, key):
        return self.zones[key]

    def names(self):
        result = set()
        for zone in self.zones:
            result.add(zone.name)
        return result

    def types(self):
        result = set()
        for zone in self.zones:
            result.add(zone.type)
        return result

    def min_corner(self):
        result = self.zones[0].min_corner()
        for zone in self.zones[1:]:
            result = result.min_corner(zone.min_corner())
        return result

    def max_corner(self):
        result = self.zones[0].max_corner()
        for zone in self.zones[1:]:
            result = result.max_corner(zone.max_corner())
        return result

    def overlaping_zones(self):
        for i in range(len(self.zones)):
            a = self.zones[i]
            for b in self.zones[i+1:]:
                overlap = a.overlaping_zone(b)
                if overlap:
                    yield overlap

    def remove_overlaps(self):
        work = list(self.zones)

        outer_i = 0
        while outer_i < len(work):
            outer = work[outer_i]

            seen = work[:outer_i+1]
            remaining = work[outer_i+1:]
            new_remaining = []

            for inner in remaining:
                overlap = outer.overlaping_zone(inner)

                if overlap:
                    non_overlaps = inner.split_by_overlap(overlap)
                    self.zone_counts[inner.original_id] += len(non_overlaps) - 1
                    if self.zone_counts[inner.original_id] == 0:
                        print("WARNING: TOTAL ECLIPSE of {} by {}!".format(inner, outer))
                    new_remaining += non_overlaps

                else:
                    new_remaining.append(inner)

            work = seen + new_remaining
            outer_i += 1

        self.zones = work

    def optimize(self):
        """Merge zones of the same ID to speed up searches later.

        Must remove overlaps before running, or this is pointless!
        """
        # Map out the zones by ID so we can focus on merging zones of the same ID first.
        to_optimize_by_id = {}
        for zone in self.zones:
            oid = zone.original_id
            if oid not in to_optimize_by_id:
                to_optimize_by_id[zone.original_id] = []
            to_optimize_by_id[zone.original_id].append(zone)

        # Optimize one ID at a time
        for zones_with_same_id in to_optimize_by_id.values():
            self._optimize_same_id_only(zones_with_same_id)

        # Reconstruct the list of zones
        self.zones = []
        for zones_with_same_id in to_optimize_by_id.values():
            self.zones += zones_with_same_id

    def _optimize_same_id_only(self, zones):
        """Helper method for self.optimize().

        zones provided must share the same ID.
        """
        # Temporary to see how well this version works
        self._optimize_same_id_brute_force(zones)

    def _optimize_same_id_brute_force(self, zones):
        """Reduce the zones required to represent an area.

        Find all ways to combine zones, then find the merged_combinations
        of those that result in no losses or overlaps.
        """
        merged_combinations = {1: {}}
        all_ids = set()
        for i in range(len(zones)):
            # Individual zones are groups of one.
            zone_ids = frozenset({i})
            zone = zones[i]
            merged_combinations[1][zone_ids] = zone

            # We'll need a set of all IDs later.
            all_ids.add(i)

        # Get all possible merged_combinations of parts; start at 2 (having completed 1) and count to the max size
        for merge_level in range(2, len(zones) + 1):
            # Looking for groups of merge_level
            merged_combinations[merge_level] = {}
            for lower_level in range(1, merge_level // 2 + 1):
                # Doing so be combining (lower_group, upper_group)
                upper_level = merge_level - lower_level
                # The lists of merge levels to merge
                lower_group = merged_combinations[lower_level]
                upper_group = merged_combinations[upper_level]
                for upper_ids, upper_zone in upper_group.items():
                    for lower_ids, lower_zone in lower_group.items():
                        if upper_zone is lower_zone:
                            # Not actually a merge, skip
                            continue

                        merged_ids = upper_ids | lower_ids
                        if merged_ids in merged_combinations[merge_level]:
                            # Same merged zone already found
                            continue
                        if len(merged_ids) != merge_level:
                            # Some IDs were in common, so this isn't the merge_level we're looking for
                            continue

                        merged = upper_zone.merge(lower_zone)
                        if merged is None:
                            # Couldn't merge, skip
                            continue
                        merged_combinations[merge_level][merged_ids] = merged

        # Find result with fewest possible zones (mostly max levels)
        zones.clear()
        for zone in self._merge_with_max_levels(merged_combinations, [], all_ids):
            zones.append(zone)

    def _merge_with_max_levels(self, merged_combinations, result_so_far, remaining_ids):
        """Part of self._optimize_same_id_brute_force(zones).

        Minimal zones are returned by searching for the largest merged zones first,
        and returning the first result to have exactly one of each part.
        In a worst case scenario, the original parts are returned.

        Returns the best solution (list of zones), or None (to continue searching).
        """
        # Start with the max possible merge level and count down to and including 1
        for merge_level in range(len(remaining_ids), 0, -1):
            for merged_ids, merged_zone in merged_combinations[merge_level].items():
                if merged_ids.difference(remaining_ids):
                    # Overlap detected; not allowed even in the same ID
                    continue

                new_remaining = remaining_ids.difference(merged_ids)
                if len(new_remaining) == 0:
                    # Best result!
                    return result_so_far + [merged_zone]

                best_result = self._merge_with_max_levels(merged_combinations, result_so_far + [merged_zone], new_remaining)
                if best_result:
                    # That recursion got the best result!
                    return best_result

                # Oh, ok. Keep searching the next level down then.

        # None found with this recursion
        return None

    def get_tree(self):
        return ZoneTree(self.zones)

    def __repr__(self):
        return "ZoneManager({})".format(self.zones)

