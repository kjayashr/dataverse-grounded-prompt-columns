"""Functional prompt-column Test: real instruction -> gpt-4.1 -> real citations.

Makes the Edit-prompt pop-up actually run. The instruction is authored with the
{Account.name} column token (nothing hard-coded); the runtime resolves it to the
current record before the model sees it, exactly like a real prompt column.

Advanced mode runs the Dataverse AppIQ MCP tools. Which tools are active is the
maker's choice in the pop-up (Auto = all; or a chosen subset). Two live calls:

  1. retrieval  -- search_data (semantic over notes/files) + read_query (relational)
     + records.retrieve (to cite). search_data is disabled on the trial, so the
     semantic step is a live LLM meaning-match over the account's real notes; the
     records, ids and citations are real. If the maker turns search_data off, the
     notes drop out and the answer degrades to structured-only -- the value of
     semantic search, shown live.
  2. prompt column -- resolved instruction + selected grounding -> the answer.

Default mode grounds only on the account row's own columns.
"""
import json
import re

from . import semantic
from .llm import chat
from .records import link

_INDUSTRY = "Manufacturing"
_REVENUE = "$2,000,000"

# The Dataverse MCP read tools surfaced in the pop-up (real tool names, preview
# June 2026). A prompt column is read-only grounding, so only these are exposed;
# the write/delete tools (create_record, update_record, delete_record, *_table)
# are deliberately withheld.
TOOLS = [
    {"id": "search_data", "label": "Semantic search over notes, emails, files (needs Dataverse search on)"},
    {"id": "search", "label": "Keyword search across records and metadata"},
    {"id": "read_query", "label": "Relational query, JOINs and aggregates (SELECT)"},
    {"id": "fetch", "label": "Retrieve a full record to cite"},
    {"id": "describe_table", "label": "Inspect table schema: columns, types, relationships"},
    {"id": "list_tables", "label": "Discover the tables available in the environment"},
]
_TOOL_IDS = [t["id"] for t in TOOLS]


def resolve(instruction, account):
    """Substitute the {Account.name} column token with the current record's value."""
    text = (instruction or "").strip() or semantic.PROMPT_COLUMN
    text = re.sub(r"[\{\[]\s*Account\.name\s*[\]\}]", account, text, flags=re.IGNORECASE)
    text = re.sub(r"\bAccount\.name\b", account, text, flags=re.IGNORECASE)
    return text


def _pool(org_base, tools):
    """The account's real linked records, filtered by which tools are active."""
    active = tools if tools else _TOOL_IDS  # Auto (empty) means all tools
    use_semantic = "search_data" in active
    use_struct = ("read_query" in active) or ("search" in active)
    pool = []
    if use_semantic:
        pool += [{"type": "note", "label": n["label"], "meta": n["meta"],
                  "url": link(org_base, "annotation", n["id"])} for n in semantic._NOTES]
    if use_struct:
        pool += [{"type": s["type"], "label": s["label"], "meta": s["meta"],
                  "url": link(org_base, s["type"], s["id"])} for s in semantic._REL_SOURCES]
    return pool


def _parse_indices(raw, n):
    m = re.search(r"\[[\d,\s]*\]", raw)
    if m:
        try:
            got = [int(i) for i in json.loads(m.group(0))]
            got = [i for i in got if 0 <= i < n]
            if got:
                return got
        except (ValueError, json.JSONDecodeError):
            pass
    return list(range(n))


def _retrieval_label(tools):
    active = [t for t in (tools or _TOOL_IDS) if t in ("search_data", "read_query", "search", "fetch")]
    names = ", ".join(active) or "(no retrieval tools selected)"
    return f"retrieval via {names}  (search_data is an LLM meaning-match, disabled on trial)"


def run(s, mode, instruction, tools=None):
    org_base = s.org_web_base
    account = semantic.ACCOUNT
    account_url = link(org_base, "account", semantic.ACCOUNT_ID)
    tools = [t for t in (tools or []) if t in _TOOL_IDS]
    resolved = resolve(instruction, account)

    if mode == "advanced":
        pool = _pool(org_base, tools)
        if pool:
            listing = "\n".join(f"[{i}] {r['type']}: {r['label']} - {r['meta']}"
                                for i, r in enumerate(pool))
            sel_user = (f"Task: {resolved}\n\nAccount: {account}\n\n"
                        f"Records linked to this account:\n{listing}\n\n"
                        "Return the indices of the records relevant to the task as a JSON array "
                        "of integers, e.g. [0,2]. Return only the array.")
            sel_msgs = [
                {"role": "system", "content":
                 "You are the retrieval step of a Dataverse agent, standing in for search_data "
                 "(semantic search over notes and files) plus a query over related records. "
                 "Choose which of the listed records are relevant to the task."},
                {"role": "user", "content": sel_user},
            ]
            raw_sel = chat(s, sel_msgs, max_tokens=40, temperature=0)
            idx = _parse_indices(raw_sel, len(pool))
            selected = [pool[i] for i in idx]
            grounding = "\n".join(f"- {r['type']}: {r['label']} - {r['meta']}" for r in selected)
            retrieval_step = {"tool": _retrieval_label(tools), "request": sel_user, "response": raw_sel}
        else:
            selected, grounding = [], ""
            retrieval_step = {"tool": _retrieval_label(tools),
                              "request": "(no retrieval tools selected)",
                              "response": "no records retrieved"}

        gen_user = (f"{resolved}\n\nGrounding retrieved from your Dataverse via AppIQ tools "
                    f"(cite what you use):\n{grounding or '(none)'}")
        gen_msgs = [
            {"role": "system", "content":
             "You are an AI Builder prompt column running per row. Follow the instruction "
             "exactly. Ground your answer only in the retrieved records provided; do not "
             "invent facts. Be specific about the risk signals you found."},
            {"role": "user", "content": gen_user},
        ]
        answer = chat(s, gen_msgs, max_tokens=150, temperature=0.3)
        return {
            "account": account, "account_url": account_url, "mode": mode,
            "instruction": instruction, "resolved": resolved, "tools": tools or _TOOL_IDS,
            "answer": answer, "sources": selected,
            "trace": [retrieval_step,
                      {"tool": "prompt column generation  (gpt-4.1, per row)",
                       "request": gen_user, "response": answer}],
        }

    # default: grounded on the current record's own columns only.
    cols = f"name: {account}\nindustry: {_INDUSTRY}\nannual revenue: {_REVENUE}"
    gen_user = f"{resolved}\n\nCurrent record columns:\n{cols}"
    gen_msgs = [
        {"role": "system", "content":
         "You are an AI Builder prompt column grounded only on the current record's own "
         "columns (this record). Follow the instruction. Do not invent related records, "
         "notes, or deals you were not given."},
        {"role": "user", "content": gen_user},
    ]
    answer = chat(s, gen_msgs, max_tokens=120, temperature=0.3)
    return {
        "account": account, "account_url": account_url, "mode": mode,
        "instruction": instruction, "resolved": resolved, "tools": [],
        "answer": answer, "sources": [],
        "trace": [{"tool": "prompt column generation  (this record, gpt-4.1)",
                   "request": gen_user, "response": answer}],
    }
