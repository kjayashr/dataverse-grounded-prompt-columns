"""The semantic-search value demo: three ways to ground the same account.

Everything here is real. On Fabrikam (org406c2541) we seeded three notes whose
risk signals are written in plain language. Then:
  - keyword search for risk/churn/renewal over those notes returns 0 (verified),
  - relationship grounding reads only the linked opportunities/contacts and sees
    a healthy pipeline (low risk),
  - semantic retrieval reads the notes by meaning and catches the churn signal
    (high risk), citing the real note records.

The reversal (structured says low, semantic says high) is the point: it is the
value of semantic search, which keyword and relationship grounding cannot show.

Note on the retrieval engine: Dataverse Search is disabled on the trial, and it
is keyword/full-text anyway. The semantic step here is an LLM meaning-match over
the real note text; when the team's search_data / semantic search is enabled it
drops in as the retrieval engine. The records cited are real; the keyword-fails
and relationship-misses are real queries.
"""
from .records import link

ACCOUNT = "Fabrikam, Inc."
ACCOUNT_ID = "88cea450-cb0c-ea11-a813-000d3a1b1223"

# The real seeded notes (annotation ids from the org).
_NOTES = [
    {"label": "Plant visit debrief", "id": "7f1e18c4-a07c-f111-ab0e-6045bd07969f",
     "meta": "\"unhappy after the recall, now comparing a competitor for next year\""},
    {"label": "Budget conversation", "id": "841e18c4-a07c-f111-ab0e-6045bd07969f",
     "meta": "\"next year's capital budget is on hold pending a cost review\""},
    {"label": "Follow-up attempt", "id": "891e18c4-a07c-f111-ab0e-6045bd07969f",
     "meta": "\"two voicemails and an email over three weeks, no reply\""},
]

_REL_SOURCES = [
    {"type": "opportunity", "label": "2 Café Duo Espresso Machines", "meta": "$25,800 · open · 90%",
     "id": "90a128af-1f73-ea11-a811-000d3a1bb5a2"},
    {"type": "contact", "label": "Haroun Stormonth", "meta": "Production Head",
     "id": "cdd6a450-cb0c-ea11-a813-000d3a1b1223"},
]


def get_semantic(org_base):
    def notes():
        return [{"type": "note", "label": n["label"], "meta": n["meta"],
                 "url": link(org_base, "annotation", n["id"])} for n in _NOTES]

    def rel():
        return [{**s, "url": link(org_base, s["type"], s["id"])} for s in _REL_SOURCES]

    return {
        "account": ACCOUNT,
        "account_url": link(org_base, "account", ACCOUNT_ID),
        "tiers": [
            {"key": "keyword", "title": "Keyword search",
             "how": "Search the notes for the words “risk”, “churn”, “renewal”",
             "found": "0 of 3 notes", "verdict": "none", "verdict_label": "No risk detected",
             "summary": "The signals are written in plain language, so a literal keyword search "
                        "returns nothing and reports no concern. It cannot see meaning.",
             "sources": []},
            {"key": "relationship", "title": "Relationship / columns",
             "how": "Read the account's linked opportunities and contacts",
             "found": "structured records only", "verdict": "low", "verdict_label": "Low risk",
             "summary": "$25,800 in open pipeline, $238,498 recently won, engaged buyers. The "
                        "structured data looks healthy, so this reports low risk. It never reads "
                        "the notes, so it misses what is actually happening.",
             "sources": rel()},
            {"key": "semantic", "title": "Semantic search",
             "how": "Retrieve records that mean “renewal risk”, across unstructured text",
             "found": "3 of 3 notes", "verdict": "high", "verdict_label": "High risk",
             "summary": "Reading the notes by meaning, semantic search catches active churn signals "
                        "that keyword and relationship grounding both miss: frustration after a "
                        "product recall with a competitor now under evaluation, next year's budget "
                        "frozen, and three weeks of unanswered outreach. The verdict flips to high "
                        "risk. Recommend exec escalation.",
             "sources": notes()},
        ],
        "reversal": "Same account. The structured data said low risk. Semantic search read the "
                    "notes and caught the churn signal that flips it to high risk.",
    }
