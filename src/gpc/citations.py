"""Citations (feature F2) and the reverse index for cheap refresh (feature F3).

`sources_column` is what we persist next to the value, the `<col>_Sources`
column: the exact records the answer was built from, so a reviewer can verify it.

`ReverseIndex` maps each source record to the cells that cited it, so when a
record changes we can find the affected cells without scanning every row.
"""


def sources_column(used_sources):
    """The persisted citation payload for one cell."""
    return [{"n": i, "ref": s.ref, "kind": s.kind, "label": s.label}
            for i, s in enumerate(used_sources, 1)]


class ReverseIndex:
    def __init__(self):
        self._by_ref = {}   # source ref -> set of account ids that cited it

    def record(self, account_id, used_sources):
        for s in used_sources:
            self._by_ref.setdefault(s.ref, set()).add(account_id)

    def dependents(self, ref):
        return set(self._by_ref.get(ref, set()))

    def size(self):
        return sum(len(v) for v in self._by_ref.values())
