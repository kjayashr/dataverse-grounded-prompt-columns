"""Incremental refresh (feature F3): recompute only what changed.

The expensive step is generation. So refresh runs cheap retrieval to compute each
cell's current fingerprint and compares it to the stored one. Only cells whose
sources actually changed (a cited record updated, or a new relevant record
appeared) are regenerated. Everything else is skipped for free.

This is the "spreadsheet" behavior: change one number, only the formulas that
used it recalculate.
"""
from . import ground as G
from . import enrich as E


def incremental_refresh(store, mode="grounded", principal=None, client=None, model=None):
    recomputed, skipped = [], []
    checks = 0
    spent = 0.0

    for account_id, prev in list(store.results.items()):
        checks += 1
        # cheap: re-run retrieval only, to see if the source set changed
        current = G.ground(account_id, principal=principal)
        if G.fingerprint(current) == prev.fingerprint:
            skipped.append(account_id)
            continue
        # changed: pay for one generation
        from . import mockdata
        account = mockdata.account_by_id(account_id)
        r, _ = E.enrich_cell(account, mode, principal, client, model)
        store.put(r, current)
        spent += r.credits
        recomputed.append(account_id)

    return {
        "checks": checks,              # cheap retrieval checks (no generation cost)
        "recomputed": recomputed,      # cells that changed and were regenerated
        "skipped": skipped,            # cells with no change, cost 0
        "credits": round(spent, 3),
    }
