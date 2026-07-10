"""Snapshot of REAL records captured from the Sales Trial org (org406c2541).

This is not invented data: every account, value, and record id was pulled from
Dataverse. Serving it lets the container run with no credentials while still
showing real, clickable citations. Live mode (dataverse.py) re-derives the same
shape from a fresh query.
"""
from .records import link

# name, revenue, risk, openV, wonV, grounded, sources[type,label,meta,id]
_SNAPSHOT = [
    {"name": "Fabrikam, Inc.", "revenue": 8000000, "risk": "low", "openV": 25800, "wonV": 238498,
     "grounded": "Fabrikam, Inc. has $25,800 in open pipeline across 1 deal (largest: 2 Café Duo Espresso Machines at $25,800, 90% confidence), plus $238,498 recently won. Renewal risk low: keep the active deal moving and re-engage the buying contacts.",
     "sources": [
        {"type": "opportunity", "label": "2 Café Duo Espresso Machines", "meta": "$25,800 · open · 90%", "id": "90a128af-1f73-ea11-a811-000d3a1bb5a2"},
        {"type": "opportunity", "label": "10 Café A-100 Automatic Espresso Machines", "meta": "$96,500 · won", "id": "a6633961-011e-4806-ba99-2f883d766a86"},
        {"type": "opportunity", "label": "12 Café A-100 Automatic Espresso Machines", "meta": "$114,000 · won", "id": "8e812dad-038a-4e64-b74f-4adf4703d91d"},
        {"type": "contact", "label": "Haroun Stormonth", "meta": "Production Head", "id": "cdd6a450-cb0c-ea11-a813-000d3a1b1223"},
        {"type": "contact", "label": "Zoltán Szabó", "meta": "Sales Manager", "id": "be755968-65a5-ea11-a812-000d3a8b3ec6"}]},
    {"name": "Trey Research", "revenue": 300000, "risk": "low", "openV": 172500, "wonV": 862700,
     "grounded": "Trey Research has $172,500 in open pipeline across 2 deals (largest: 50 Café A-100 Automatic at $95,000, 83% confidence), plus $862,700 recently won. Renewal risk low: strong momentum, keep the active deals moving.",
     "sources": [
        {"type": "opportunity", "label": "5 Café A-100 Automatic", "meta": "$77,500 · open", "id": "14741c9e-4b9e-ea11-a811-000d3a1bb122"},
        {"type": "opportunity", "label": "50 Café A-100 Automatic", "meta": "$95,000 · open", "id": "3e815937-cf53-4184-885e-389ec2fd0ae3"},
        {"type": "opportunity", "label": "30 Café A-100 Automatic; 3 Cafe Duo", "meta": "won", "id": "d64bff17-c3ef-4785-b917-53b987b9ef11"},
        {"type": "opportunity", "label": "20 Café A-100 Automatic", "meta": "$167,000 · won", "id": "0fe9d18d-608e-4d80-b9a7-ed2dd79a1ba6"}]},
    {"name": "Northwind Traders", "revenue": 6800000, "risk": "low", "openV": 89377, "wonV": 0,
     "grounded": "Northwind Traders has $89,377 in open pipeline across 4 deals (largest: 2 Café Corto at $33,800, 90% confidence), and no recent wins. Renewal risk low, but no closed business yet: push the open deals to close.",
     "sources": [
        {"type": "opportunity", "label": "18 Airpot Coffee Makers", "meta": "open", "id": "b052fc98-e8f0-ea11-a815-000d3a1b14a2"},
        {"type": "opportunity", "label": "2 Café Corto", "meta": "$33,800 · open · 90%", "id": "2ec06197-31ec-ea11-a817-000d3a1b14a2"},
        {"type": "opportunity", "label": "5 Café BG-1 Pro Grinders", "meta": "open", "id": "3cbbd39d-d3f0-ea11-a815-000d3a33f3c3"},
        {"type": "opportunity", "label": "1 Café PG-1 Pro Grinders", "meta": "open", "id": "4cbbd68d-d3f0-ea11-a815-000d3a42f5c8"}]},
    {"name": "Alpine Ski House", "revenue": 4830000, "risk": "low", "openV": 24889, "wonV": 427950,
     "grounded": "Alpine Ski House has $24,889 in open pipeline across 3 deals (largest: 1 Café Grande Espresso Machine at $14,900, 72% confidence), plus $427,950 recently won. Renewal risk low: healthy history, modest active pipeline.",
     "sources": [
        {"type": "opportunity", "label": "10 Airpot XL Coffee Makers", "meta": "open", "id": "e90a0493-e8f0-ea11-a815-000d3a1b14a2"},
        {"type": "opportunity", "label": "1 Café Grande Espresso Machine", "meta": "$14,900 · open · 72%", "id": "becc5dba-b1f1-ea11-a815-000d3a1b14a2"},
        {"type": "opportunity", "label": "1 Café BG-1 Grinder", "meta": "open", "id": "a09c2889-a016-eb11-a813-002248029f77"},
        {"type": "opportunity", "label": "50 Café BG-1 coffee Grinder", "meta": "$249k · won", "id": "bc1cb5e4-9bab-4151-a10f-c2eb9c1d30c9"}]},
    {"name": "A. Datum Corporation", "revenue": 35000000, "risk": "low", "openV": 120491, "wonV": 0,
     "grounded": "A. Datum Corporation has $120,491 in open pipeline across 3 deals (largest: 3 Café Grande Espresso Machines at $44,700, 83% confidence), and no recent wins. Large account ($35M revenue): prioritize closing the open pipeline.",
     "sources": [
        {"type": "opportunity", "label": "9 Café PG-1 Grinders", "meta": "open", "id": "87a328af-1f73-ea11-a811-000d3a1bb5a2"},
        {"type": "opportunity", "label": "3 Café Grande Espresso Machines", "meta": "$44,700 · open · 83%", "id": "71ecca72-0d1c-48ce-a21b-0d6650b1e904"},
        {"type": "opportunity", "label": "2 Semiautomatic Espresso Machines", "meta": "open", "id": "9d3d18ff-5104-4173-9ed5-b1805793eea4"},
        {"type": "contact", "label": "Kevin Martin", "meta": "Sales Manager", "id": "678c7b32-3f72-ea11-a811-000d3a1b1f2c"}]},
    {"name": "Fourth Coffee", "revenue": 8000000, "risk": "medium", "openV": 0, "wonV": 25800,
     "grounded": "Fourth Coffee has $25,800 in recently won deals and no open pipeline in flight. With nothing active ahead of renewal, proactive outreach is recommended to re-open the relationship.",
     "sources": [
        {"type": "opportunity", "label": "2 Café Duo for Fourth Coffee", "meta": "$25,800 · won", "id": "b751444c-cf81-4d6d-b89a-684a8ef20557"},
        {"type": "contact", "label": "Carole Poland", "meta": "Sales Manager", "id": "255de5a8-56d0-ea11-a812-000d3a1bbd52"}]},
    {"name": "Contoso Manufacturing", "revenue": None, "risk": "medium", "openV": 0, "wonV": 0,
     "grounded": "Contoso Manufacturing has no open pipeline and no closed deals on record. As a new/empty account, it needs a proactive outreach and discovery motion before any renewal conversation.",
     "sources": []},
]


def _baseline(name, revenue):
    rev = "n/a" if revenue is None else "$" + format(int(revenue), ",")
    tail = f" with annual revenue {rev}." if revenue is not None else " in your CRM."
    return f"{name} is an account{tail} Standard renewal risk applies; recommend timely engagement."


def get_accounts(org_base):
    out = []
    for a in _SNAPSHOT:
        rec = dict(a)
        rec["baseline"] = _baseline(a["name"], a["revenue"])
        rec["sources"] = [{**s, "url": link(org_base, s["type"], s["id"])} for s in a["sources"]]
        out.append(rec)
    return out
