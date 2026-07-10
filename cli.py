#!/usr/bin/env python3
"""Grounded Prompt Columns: command-line demo.

Runs with the standard library only. No org, no pip install needed.

  python3 cli.py demo                 grounded, cited answers for every account
  python3 cli.py demo --baseline      what a same-row prompt column shows today
  python3 cli.py compare contoso      baseline vs grounded, side by side
  python3 cli.py sources contoso      the citations behind one cell
  python3 cli.py secure contoso       same cell, full vs restricted permissions
  python3 cli.py refresh              backfill, change one record, refresh cheaply
"""
import argparse
import os
import sys
import textwrap

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from gpc import mockdata
from gpc import ground as G
from gpc import enrich as E
from gpc import refresh as R
from gpc import cost as COST

RISK_MARK = {"high": "[HIGH]", "medium": "[MED ]", "low": "[LOW ]", "unknown": "[ -- ]"}


def _wrap(text, width, indent):
    lines = textwrap.wrap(text, width)
    pad = " " * indent
    return ("\n" + pad).join(lines) if lines else ""


def cmd_demo(args):
    mode = "baseline" if args.baseline else "grounded"
    accounts = mockdata.all_accounts()
    store, summary = E.enrich_view(accounts, mode=mode)
    title = "Renewal Risk column, TODAY (same-row only)" if args.baseline else \
            "Renewal Risk column, GROUNDED + CITED"
    print("\n" + title)
    print("=" * 74)
    for a in accounts:
        r = store.results[a["id"]]
        cites = "" if args.baseline else f"   ({len(r.sources)} sources)"
        print(f"\n{RISK_MARK[r.risk]} {r.name}{cites}")
        print("        " + _wrap(r.value, 62, 8))
    print("\n" + "-" * 74)
    print(f"cells: {summary['generations']}   "
          f"generation calls: {summary['generations']}   "
          f"credits: {summary['credits']} (${summary['dollars']})")
    if not args.baseline:
        print("tip: `python3 cli.py refresh` to see incremental, low-cost refresh.")


def cmd_compare(args):
    a = mockdata.account_by_id(args.account)
    base, _ = E.enrich_cell(a, mode="baseline")
    grnd, _ = E.enrich_cell(a, mode="grounded")
    print(f"\n{a['name']}: BASELINE vs GROUNDED")
    print("=" * 74)
    print("\nBASELINE (same row only), no sources:")
    print("   " + _wrap(base.value, 66, 3))
    print(f"\nGROUNDED {RISK_MARK[grnd.risk]}, {len(grnd.sources)} cited sources:")
    print("   " + _wrap(grnd.value, 66, 3))
    print("\nCited records:")
    for s in grnd.sources:
        print(f"   [{s['n']}] {s['label']}   <{s['ref']}>")


def cmd_sources(args):
    a = mockdata.account_by_id(args.account)
    r, _ = E.enrich_cell(a, mode="grounded")
    print(f"\n{a['name']} {RISK_MARK[r.risk]}")
    print("   " + _wrap(r.value, 66, 3))
    print("\n_Sources column (persisted provenance):")
    for s in r.sources:
        print(f"   [{s['n']}] {s['kind']:<11} {s['label']}   <{s['ref']}>")


def cmd_secure(args):
    a = mockdata.account_by_id(args.account)
    full, _ = E.enrich_cell(a, mode="grounded", principal=G.FULL)
    rest, _ = E.enrich_cell(a, mode="grounded", principal=G.RESTRICTED)
    print(f"\n{a['name']}: security-trimmed grounding")
    print("=" * 74)
    print(f"\nFULL access ({len(full.sources)} sources) {RISK_MARK[full.risk]}:")
    print("   " + _wrap(full.value, 66, 3))
    print(f"\nRESTRICTED user ({len(rest.sources)} sources) {RISK_MARK[rest.risk]}:")
    print("   " + _wrap(rest.value, 66, 3))
    print("\nThe restricted user can only ground on records they may read.")


def cmd_refresh(args):
    accounts = mockdata.all_accounts()
    store, summary = E.enrich_view(accounts, mode="grounded")
    n = summary["generations"]
    print("\nStep 1: backfill every account (grounded + cited)")
    print(f"   {n} accounts generated, {summary['credits']} credits (${summary['dollars']})")

    print("\nStep 2: a new high-severity case is opened at Contoso Ltd")
    mockdata.add_case("contoso", {"ref": "incident/3b9", "title": "Safety recall",
                                  "severity": "high", "status": "open", "age_days": 0})

    print("\nStep 3: incremental refresh (recompute only what changed)")
    report = R.incremental_refresh(store, mode="grounded")
    print(f"   checked {report['checks']} cells with cheap retrieval (no generation cost)")
    print(f"   recomputed: {report['recomputed']}  ({len(report['recomputed'])} generation call)")
    print(f"   skipped:    {len(report['skipped'])} cells, no change, cost 0")
    print(f"   refresh cost: {report['credits']} credits (${COST.dollars(report['credits'])})")

    blind = n
    print("\nCompare:")
    print(f"   blind full refresh = {blind} generations")
    print(f"   incremental        = {len(report['recomputed'])} generation")
    print("   same freshness, a fraction of the cost.")
    print("\nContoso now reads:")
    print("   " + _wrap(store.results['contoso'].value, 66, 3))


def main():
    p = argparse.ArgumentParser(description="Grounded Prompt Columns demo")
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("demo", help="grounded answers for every account")
    d.add_argument("--baseline", action="store_true", help="show today's same-row behavior")
    d.set_defaults(func=cmd_demo)

    c = sub.add_parser("compare", help="baseline vs grounded for one account")
    c.add_argument("account"); c.set_defaults(func=cmd_compare)

    s = sub.add_parser("sources", help="citations for one account")
    s.add_argument("account"); s.set_defaults(func=cmd_sources)

    se = sub.add_parser("secure", help="full vs restricted permissions")
    se.add_argument("account"); se.set_defaults(func=cmd_secure)

    r = sub.add_parser("refresh", help="backfill, change a record, refresh cheaply")
    r.set_defaults(func=cmd_refresh)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
