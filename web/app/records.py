"""Grounding + summarization logic, shared by mock and live modes.

Given an account and its related opportunities/contacts, produce the baseline
(same-row) text, the grounded summary derived from the real numbers, and the
citation set (with deep-link URLs to the real records). This mirrors the
retrieve -> generate -> cite pipeline; in the proposed native feature the
generation step is the AI Builder prompt, here it is deterministic so the demo
runs without a model.
"""


def _money(n):
    return "n/a" if n is None else "$" + format(int(n), ",")


def link(org_base, entity, rid):
    return f"{org_base}{entity}&id={rid}"


def summarize(name, revenue, opps, contacts, org_base):
    """opps: [{name,val,state,prob,id}] (state 0=open, 1=won).
    contacts: [{name,title,id}]. Returns the API record dict."""
    open_ = [o for o in opps if o.get("state") == 0]
    won = [o for o in opps if o.get("state") == 1]
    open_v = sum(o.get("val") or 0 for o in open_)
    won_v = sum(o.get("val") or 0 for o in won)
    largest = max(open_, key=lambda o: o.get("val") or 0, default=None)
    avg_prob = round(sum(o.get("prob") or 0 for o in open_) / len(open_)) if open_ else 0
    risk = "medium" if not open_ else ("low" if avg_prob >= 70 else "medium")

    sources = []
    for o in opps[:4]:
        state_txt = "won" if o.get("state") == 1 else "open"
        sources.append({
            "type": "opportunity",
            "label": (o.get("name") or "").strip(),
            "meta": f"{_money(o.get('val'))} · {state_txt}"
                    + (f" · {o['prob']}%" if o.get("prob") and o.get("state") == 0 else ""),
            "url": link(org_base, "opportunity", o["id"]),
        })
    for c in contacts[:2]:
        sources.append({
            "type": "contact",
            "label": c.get("name") or "",
            "meta": c.get("title") or "contact",
            "url": link(org_base, "contact", c["id"]),
        })

    if not open_:
        grounded = (f"{name} has {_money(won_v)} in recently won deals and no open pipeline "
                    f"in flight. With nothing active ahead of renewal, proactive outreach is "
                    f"recommended to re-open the relationship.")
    else:
        grounded = (f"{name} has {_money(open_v)} in open pipeline across {len(open_)} "
                    f"deal{'s' if len(open_) != 1 else ''} (largest: {largest['name'].strip()} "
                    f"at {_money(largest.get('val'))}, {avg_prob}% avg confidence), plus "
                    f"{_money(won_v)} recently won. Renewal risk {risk}: keep the active deals "
                    f"moving and re-engage the buying contacts.")

    baseline = (f"{name} is an account"
                + (f" with annual revenue {_money(revenue)}." if revenue is not None else " in your CRM.")
                + " Standard renewal risk applies; recommend timely engagement.")

    return {
        "name": name, "revenue": revenue, "risk": risk,
        "openV": open_v, "wonV": won_v,
        "baseline": baseline, "grounded": grounded, "sources": sources,
    }
