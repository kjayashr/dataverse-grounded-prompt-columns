"""Grounding: the security-trimmed retrieval step (feature F1).

`ground(account_id, principal)` gathers the related records an account's answer
should be built from: cases, opportunities, activities, contacts, files. In live
mode this is `search_data` / related-table retrieval run under the caller's
privileges. Here it reads mock data and applies a simple ACL so we can show
security trimming: a restricted principal provably sees fewer sources.

Each returned Source has:
  ref  : stands in for the Dataverse row id (used as the citation)
  kind : incident | opportunity | contact | activity | file
  label/meta : human text for the citation
  signals    : structured facts the generator reasons over
  sig        : a content signature, so refresh can tell if the source changed
"""
from dataclasses import dataclass, field


@dataclass
class Source:
    ref: str
    kind: str
    label: str
    meta: str
    signals: dict = field(default_factory=dict)

    @property
    def sig(self):
        # content signature: ref plus the signal values that would change the answer
        return self.ref + "|" + "|".join(f"{k}={v}" for k, v in sorted(self.signals.items()))


# A principal is just the set of record kinds it is allowed to read.
FULL = {"incident", "opportunity", "contact", "activity", "file"}
RESTRICTED = {"opportunity", "activity"}  # e.g. a user without case/file access


def ground(account_id, principal=None, budget=8):
    """Return the ranked, deduped, budget-capped sources for an account,
    filtered to what `principal` is allowed to see (security trimming)."""
    from . import mockdata
    allowed = principal if principal is not None else FULL
    rel = mockdata.related(account_id)
    out = []

    for c in rel["cases"]:
        if "incident" not in allowed:
            continue
        out.append(Source(c["ref"], "incident", f'Case: {c["title"]}',
                          f'{c["severity"]} severity, {c["status"]}, {c["age_days"]}d',
                          {"severity": c["severity"], "status": c["status"], "age": c["age_days"]}))
    for o in rel["opps"]:
        if "opportunity" not in allowed:
            continue
        out.append(Source(o["ref"], "opportunity", f'Opp: {o["name"]} (${o["amount"]:,})',
                          f'stage {o["stage"]}, no activity {o["last_activity_days"]}d',
                          {"amount": o["amount"], "idle": o["last_activity_days"], "stage": o["stage"]}))
    for c in rel["contacts"]:
        if "contact" not in allowed:
            continue
        out.append(Source(c["ref"], "contact", f'{c["name"]} ({c["role"]})',
                          f'status: {c["status"]}', {"status": c["status"], "role": c["role"]}))
    if rel["last_contact_days"] is not None and "activity" in allowed:
        d = rel["last_contact_days"]
        out.append(Source(f"activity/{account_id}", "activity", "Last customer contact",
                          f"{d} days ago", {"last_contact_days": d}))
    for n in rel["annotations"]:
        if "file" not in allowed:
            continue
        out.append(Source(n["ref"], "file", f'File: {n["file"]}',
                          n["note"], {"note": n["note"]}))

    # rank: risk-bearing kinds first, then cap to the retrieval budget
    order = {"incident": 0, "opportunity": 1, "contact": 2, "file": 3, "activity": 4}
    out.sort(key=lambda s: order.get(s.kind, 9))
    return out[:budget]


def fingerprint(sources):
    """A stable signature of a source set. If any cited source changes, or a new
    relevant record appears, this changes, and refresh knows to recompute."""
    return "~".join(sorted(s.sig for s in sources))
