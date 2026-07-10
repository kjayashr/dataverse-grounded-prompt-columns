"""Generation: turn the account plus its grounded sources into an answer.

In live mode `generate_live` calls the real AI Builder prompt via the Dataverse
`Predict` message (see client.py). In mock mode `generate_mock` synthesizes a
realistic Renewal Risk summary deterministically from the retrieved signals, so
the demo runs with no model and no network.

Both return an Answer(text, risk, used) where `used` is the subset of sources
the answer actually relied on, which becomes the citation set.
"""
from dataclasses import dataclass, field


@dataclass
class Answer:
    text: str
    risk: str            # high | medium | low
    used: list = field(default_factory=list)   # list[Source]


def baseline_prompt(account):
    return (f"Summarize the renewal risk for {account['name']}, a "
            f"{account['industry']} account with ARR ${account['arr']:,} "
            f"renewing on {account['renewal']}.")


def grounded_prompt(account, sources):
    lines = [baseline_prompt(account),
             "Use only the following related records, and cite them:"]
    for i, s in enumerate(sources, 1):
        lines.append(f"[{i}] {s.label} - {s.meta}")
    return "\n".join(lines)


# ---- baseline: same-row only, no grounding (what ships today) ----
def generate_baseline(account):
    txt = (f"{account['name']} is a {account['industry'].lower()} account renewing "
           f"{_date(account['renewal'])}. Standard renewal risk applies; recommend "
           f"timely engagement.")
    return Answer(txt, "unknown", [])


# ---- grounded: reason over the retrieved sources ----
def generate_mock(account, sources):
    facts, used, score = [], [], 0

    high_cases = [s for s in sources if s.kind == "incident" and s.signals.get("severity") == "high"]
    open_cases = [s for s in sources if s.kind == "incident" and s.signals.get("status") == "open"]
    if open_cases:
        n, nh = len(open_cases), len(high_cases)
        facts.append(f"{n} open case{'s' if n > 1 else ''}"
                     + (f" ({nh} high-severity)" if nh else ""))
        used += open_cases
        score += 2 * nh + n

    stalled = [s for s in sources if s.kind == "opportunity" and s.signals.get("idle", 0) > 30]
    for s in stalled:
        facts.append(f"a stalled ${s.signals['amount']:,} deal untouched for "
                     f"{s.signals['idle']} days")
        used.append(s); score += 2

    left = [s for s in sources if s.kind == "contact" and s.signals.get("status") == "left"]
    for s in left:
        facts.append(f"the {s.signals['role']} champion has left")
        used.append(s); score += 2

    act = [s for s in sources if s.kind == "activity"]
    for s in act:
        d = s.signals["last_contact_days"]
        if d >= 30:
            facts.append(f"last contact {d} days ago"); used.append(s); score += 1

    files = [s for s in sources if s.kind == "file"]
    for s in files:
        facts.append(f'notes flag "{s.signals["note"]}"'); used.append(s); score += 1

    risk = "high" if score >= 4 else "medium" if score >= 2 else "low"

    if not facts:
        text = (f"{account['name']} looks healthy: no open cases and steady engagement. "
                f"Low renewal risk ahead of {_date(account['renewal'])}.")
    else:
        head = {"high": "High risk.", "medium": "Medium risk.", "low": "Low risk."}[risk]
        joined = _join(facts)
        body = joined[0].upper() + joined[1:]
        tail = (f" Recommend exec escalation before {_date(account['renewal'])}."
                if risk == "high" else
                f" Keep engaged ahead of {_date(account['renewal'])}.")
        text = f"{head} {body}.{tail}"
    return Answer(text, risk, used)


def generate_live(account, sources, client, model_name):
    """Call the real AI Builder prompt via Predict. Returns an Answer.
    Citations are the sources we passed in (retrieval-grounded, not model-authored)."""
    prompt = grounded_prompt(account, sources)
    text = client.predict(model_name, {"prompt": prompt})
    # risk is parsed from the model text; default medium if unclear
    low = text.lower()
    risk = "high" if "high risk" in low else "low" if "low risk" in low else "medium"
    return Answer(text.strip(), risk, sources)


def _join(items):
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + ", and " + items[-1]


def _date(iso):
    m = {"01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr", "05": "May", "06": "Jun",
         "07": "Jul", "08": "Aug", "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec"}
    y, mo, d = iso.split("-")
    return f"{m.get(mo, mo)} {int(d)}"
