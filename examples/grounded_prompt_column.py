#!/usr/bin/env python3
"""Minimal end-to-end example: compute one grounded, cited Renewal Risk cell.

Run from the repo root:  python3 examples/grounded_prompt_column.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from gpc import mockdata
from gpc import enrich as E

account = mockdata.account_by_id("contoso")

# 1) retrieve (grounded) -> 2) generate -> 3) cite, all inside enrich_cell
result, sources = E.enrich_cell(account, mode="grounded")

print(f"{result.name}  [{result.risk.upper()}]")
print(result.value)
print("\nSources (would be persisted to the _Sources column):")
for s in result.sources:
    print(f"  [{s['n']}] {s['label']}  <{s['ref']}>")
print(f"\nfingerprint: {result.fingerprint[:60]}...")
print(f"credits: {result.credits}")

# In live mode you would instead do:
#   from gpc.config import Config
#   from gpc.client import DataverseClient
#   cfg = Config(org_url="https://YOURORG.crm.dynamics.com",
#                model_name="Renewal Risk Summary")
#   client = DataverseClient(cfg)
#   result, _ = E.enrich_cell(account, mode="live", client=client, model=cfg.model_name)
#   client.update_record("accounts", account_guid,
#                        {"new_renewalrisk": result.value})
