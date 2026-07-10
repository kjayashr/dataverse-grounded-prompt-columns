"""In-memory sample data that mirrors a Dynamics 365 Sales org.

Lets the prototype run end to end with no environment, so the grounded + cited +
cost-aware behavior is visible today. In live mode the same shapes come from
Dataverse and this module is unused.

Every record carries a `ref` that stands in for a Dataverse row id, so the
citations we produce point at "records" exactly as they would against live data.
"""

ACCOUNTS = [
    {"ref": "account/8f2a", "id": "contoso",   "name": "Contoso Ltd",       "industry": "Manufacturing", "arr": 40_000_000, "renewal": "2026-09-30", "owner": "Priya N"},
    {"ref": "account/1b7c", "id": "northwind", "name": "Northwind Traders", "industry": "Distribution",  "arr": 18_000_000, "renewal": "2026-08-20", "owner": "Sam O"},
    {"ref": "account/44de", "id": "fabrikam",  "name": "Fabrikam Inc",      "industry": "Retail",        "arr": 22_000_000, "renewal": "2026-10-15", "owner": "Marco R"},
    {"ref": "account/9a01", "id": "adventure", "name": "Adventure Works",   "industry": "Logistics",     "arr": 65_000_000, "renewal": "2026-11-02", "owner": "Dana K"},
    {"ref": "account/2c55", "id": "tailspin",  "name": "Tailspin Toys",     "industry": "Consumer",      "arr":  9_000_000, "renewal": "2026-12-05", "owner": "Lena V"},
    {"ref": "account/7e12", "id": "wingtip",   "name": "Wingtip Corp",      "industry": "Energy",        "arr": 51_000_000, "renewal": "2026-09-12", "owner": "Owen T"},
]

CASES = {
    "contoso":   [{"ref": "incident/3b1", "title": "Line-down escalation", "severity": "high",   "status": "open", "age_days": 22},
                  {"ref": "incident/3b2", "title": "Firmware defect",      "severity": "high",   "status": "open", "age_days": 20},
                  {"ref": "incident/3b3", "title": "Shipment delay",       "severity": "normal", "status": "open", "age_days": 12}],
    "northwind": [{"ref": "incident/4a0", "title": "Billing dispute",      "severity": "high",   "status": "open", "age_days": 31}],
    "fabrikam":  [{"ref": "incident/455", "title": "Login errors",         "severity": "normal", "status": "open", "age_days": 5}],
    "adventure": [], "tailspin": [], "wingtip": [],
}
OPPS = {
    "contoso":   [{"ref": "opportunity/a9c", "name": "Plant Expansion", "amount": 120_000, "stage": "propose", "last_activity_days": 45}],
    "northwind": [],
    "fabrikam":  [{"ref": "opportunity/b21", "name": "Store rollout",   "amount":  60_000, "stage": "develop", "last_activity_days": 8}],
    "adventure": [{"ref": "opportunity/c30", "name": "Fleet Expansion", "amount":  80_000, "stage": "propose", "last_activity_days": 6}],
    "tailspin":  [],
    "wingtip":   [{"ref": "opportunity/d44", "name": "Grid Upgrade",    "amount": 200_000, "stage": "qualify", "last_activity_days": 61}],
}
CONTACTS = {
    "contoso":   [{"ref": "contact/22d", "name": "J. Rivera", "role": "VP Ops",       "status": "left"}],
    "fabrikam":  [{"ref": "contact/71a", "name": "A. Cole",   "role": "Owner change", "status": "active"}],
    "adventure": [{"ref": "contact/88b", "name": "M. Diaz",   "role": "Exec sponsor", "status": "active"}],
    "northwind": [], "tailspin": [], "wingtip": [],
}
ACTIVITIES = {"contoso": 38, "northwind": 14, "fabrikam": 9, "adventure": 4, "tailspin": 20, "wingtip": 9}
ANNOTATIONS = {
    "contoso":   [{"ref": "annotation/77e", "file": "QBR_Q2_Contoso.pptx", "note": "evaluating competitor"}],
    "northwind": [{"ref": "annotation/90f", "file": "Account_plan.docx",   "note": "no exec sponsor named"}],
    "wingtip":   [{"ref": "annotation/aa3", "file": "email_thread.eml",    "note": "renewal budget under review"}],
    "fabrikam":  [], "adventure": [], "tailspin": [],
}


def all_accounts():
    return [dict(a) for a in ACCOUNTS]


def account_by_id(account_id):
    for a in ACCOUNTS:
        if a["id"] == account_id:
            return dict(a)
    raise KeyError(account_id)


def related(account_id):
    """Everything that lives off the account's own row."""
    return {
        "cases": [dict(c) for c in CASES.get(account_id, [])],
        "opps": [dict(o) for o in OPPS.get(account_id, [])],
        "contacts": [dict(c) for c in CONTACTS.get(account_id, [])],
        "last_contact_days": ACTIVITIES.get(account_id),
        "annotations": [dict(n) for n in ANNOTATIONS.get(account_id, [])],
    }


def add_case(account_id, case):
    """Simulate a source change (used by the incremental-refresh demo)."""
    CASES.setdefault(account_id, []).insert(0, dict(case))
