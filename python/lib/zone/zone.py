    #!/usr/bin/env python3

from copy import deepcopy
from lib.pos import Pos
from lib.zone.zone_base import ZoneBase
from lib.zone.zone_fragment import ZoneFragment

class Zone(ZoneBase):
    """A whole zone where non-standard behavior occurs.

    pos2 is being rewritten to be exclusive, not inclusive.
    """
    def __init__(self, other=None, pos=None, size=None, name=None, ztype=None, original_id=None, axis_order=None):
        super().__init__(other, pos, size)

        self.original_id = None
        self.fragments = []
        self.eclipsed_fragments = []

        # Order to process axes, such as [0, 2, 1]
        if axis_order is None:
            axis_order = list(range(len(self._pos)))

        if isinstance(other, Zone):
            self.name = other.name
            self.type = other.type
            self.original_id = other.original_id
            self.fragments = list(other.fragments)
            self.eclipsed_fragments = list(other.eclipsed_fragments)

        elif isinstance(other, dict):
            self.name = other["name"]
            self.type = other["type"]
            self.original_id = original_id
            self.fragments.append(ZoneFragment(self, axis_order=axis_order))

        elif other is None:
            self.name = name
            self.type = ztype
            self.original_id = original_id
            self.fragments.append(ZoneFragment(self, axis_order=axis_order))

        else:
            raise TypeError("Expected Zone to be initialized with a dict or another Zone")

    def split_by_overlap(self, overlap):
        """Split all fragments of this zone by an overlapping zone, removing overlap."""
        new_fragments = []
        for fragment in self.fragments:
            sub_overlap = fragment.overlaping_zone(overlap)

            if sub_overlap is None:
                new_fragments.append(fragment)
                continue

            new_fragments += fragment.split_by_overlap(sub_overlap)

        self.fragments = new_fragments

    def defragment(self):
        """Minimize the number of uneclipsed fragments.

        This operation is O(n^4), but works with only one zone's fragments at a time,
        and doesn't need to be run again. This reduces n significantly for runtime.
        """
        if len(self.fragments) < 2:
            # Nothing to do
            return

        def _defrag_optimal_merge(merged_combinations, result_so_far, remaining_ids):
            """Part of self.defragment().

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

                    best_result = _defrag_optimal_merge(merged_combinations, result_so_far + [merged_zone], new_remaining)
                    if best_result:
                        # That recursion got the best result!
                        return best_result

                    # Oh, ok. Keep searching the next level down then.

            # None found with this recursion
            return None

        merged_combinations = {1: {}}
        all_ids = set()

        for i, fragment in enumerate(self.fragments):
            # Individual fragments are groups of 1
            merged_ids = frozenset({i})
            merged_combinations[1][merged_ids] = fragment

            # We'll need a set of all IDs later.
            all_ids.add(i)

        # Get all possible merged_combinations of parts; start at 2 (having completed 1) and count to the max size
        # merge_level is the number of fragments in a grouped zone.
        # For example, if A and B are original fragments (level 1),
        # and C = A + B, C is level 2 (contains 2 original fragments).
        # If D = C + A, D is level 3 (upper_level = 2, lower_level = 1, 2 + 1)
        for merge_level in range(2, len(self.fragments) + 1):
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
                        if len(merged_ids) != merge_level:
                            # Some IDs were in common, so this isn't the merge_level we're looking for
                            continue
                        if merged_ids in merged_combinations[merge_level]:
                            # Same merged zone already found
                            continue

                        merged = upper_zone.merge(lower_zone)
                        if merged is None:
                            # Couldn't merge, skip
                            continue
                        merged_combinations[merge_level][merged_ids] = merged

        # Find result with fewest possible zones (mostly max levels)
        self.fragments = _defrag_optimal_merge(merged_combinations, [], all_ids)

########################################################################################################################
# Only needed for debug and statistics:

    def __repr__(self):
        if self: # None-zero size
            return (
                'Zone('
                + 'original_id={!r}'.format(self.original_id)
                + ', {'
                + '"name": {!r}, "type": {!r}, "pos1": {!r}, "pos2": {!r}'.format(self.name, self.type, self.pos1.list, self.pos2.list)
                + '})'
            )

        else:
            return "Zone(name={!r}, ztype={!r}, pos={!r}, size={!r})".format(self.name, self.type, self._pos, self._size)

