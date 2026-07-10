"""Orchestrator: retrieve, generate, cite, and (in live mode) write back.

`enrich_cell` computes one cell. `enrich_view` backfills a whole set of accounts
(feature F3 backfill) and keeps a Store with a fingerprint per cell plus a
reverse citation index, which the refresh step uses to recompute only what
changed.
"""
from dataclasses import dataclass, field
from . import ground as G
from . import generate as GEN
from . import citations as C
from . import cost as COST


@dataclass
class Result:
    account_id: str
    name: str
    value: str
    risk: str
    sources: list          # persisted citation payload (list[dict])
    used: list             # list[Source] actually cited
    fingerprint: str
    credits: float


class Store:
    def __init__(self):
        self.results = {}          # account_id -> Result
        self.index = C.ReverseIndex()

    def put(self, r, all_sources):
        self.results[r.account_id] = r
        self.index.record(r.account_id, r.used)


def enrich_cell(account, mode="grounded", principal=None, client=None, model=None):
    """Compute a single Renewal Risk cell. Returns (Result, all_sources)."""
    if mode == "baseline":
        ans = GEN.generate_baseline(account)
        prompt = GEN.baseline_prompt(account)
        sources = []
    else:
        sources = G.ground(account["id"], principal=principal)
        if mode == "live":
            if client is None:
                raise RuntimeError("live mode needs a Dataverse client")
            ans = GEN.generate_live(account, sources, client, model)
            prompt = GEN.grounded_prompt(account, sources)
        else:  # grounded (mock synthesis)
            ans = GEN.generate_mock(account, sources)
            prompt = GEN.grounded_prompt(account, sources)

    credits = COST.generation_credits(prompt, ans.text)
    r = Result(
        account_id=account["id"], name=account["name"], value=ans.text, risk=ans.risk,
        sources=C.sources_column(ans.used), used=ans.used,
        fingerprint=G.fingerprint(sources), credits=credits,
    )
    return r, sources


def enrich_view(accounts, mode="grounded", principal=None, client=None, model=None,
                store=None, budget_credits=None):
    """Backfill a set of accounts. Respects an optional credit budget cap (F5)."""
    store = store or Store()
    spent, generations, stopped = 0.0, 0, None
    for a in accounts:
        if budget_credits is not None and spent >= budget_credits:
            stopped = a["id"]
            break
        r, all_sources = enrich_cell(a, mode, principal, client, model)
        store.put(r, all_sources)
        spent += r.credits
        generations += 1
    summary = {
        "generations": generations,
        "credits": round(spent, 3),
        "dollars": COST.dollars(spent),
        "stopped_at_budget": stopped,
    }
    return store, summary
