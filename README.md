# Grounded Prompt Columns

A prototype that makes a Microsoft Dataverse **prompt column** *grounded*, *cited*,
and *cheap to keep fresh*, and proves the idea end to end **with no environment and
no dependencies**.

> **Disclosure.** This is an external prototype that *emulates* the proposed native
> behavior using supported, public building blocks (Dataverse related-record
> retrieval, the AI Builder `Predict` message, Web API write-back). It is not a
> change to the shipping Prompt Columns feature. It exists to demonstrate customer
> value and de-risk the design. Where each part maps to a proposed native feature
> is noted below.

## The idea in one breath

A prompt column today can only see **its own row**, so its answers are generic, have
no sources, and go stale. This prototype lets the column:

- **Ground** on the related records it is allowed to see (cases, opportunities,
  activities, contacts, files), not just one row.
- **Cite** the exact records it used, so the answer is trustworthy.
- **Refresh cheaply**: when a record changes, only the few answers that used it are
  recomputed. The rest are skipped for free.

## Quickstart (30 seconds, no install)

Requires only Python 3.10+. No pip install, no org.

```bash
python3 cli.py demo                # grounded, cited answers for every account
python3 cli.py demo --baseline     # what a same-row prompt column shows today
python3 cli.py compare contoso     # baseline vs grounded, side by side
python3 cli.py sources contoso     # the citations behind one cell
python3 cli.py secure contoso      # same cell, full vs restricted permissions
python3 cli.py refresh             # backfill, change one record, refresh cheaply
```

### What you will see

`compare contoso` puts the two side by side:

```
BASELINE (same row only), no sources:
   Contoso Ltd is a manufacturing account renewing Sep 30. Standard
   renewal risk applies; recommend timely engagement.

GROUNDED [HIGH], 7 cited sources:
   High risk. 3 open cases (2 high-severity), a stalled $120,000 deal
   untouched for 45 days, the VP Ops champion has left, ...
```

`refresh` shows the cost story: a new case at Contoso recomputes **1** cell and
skips 5, instead of regenerating all 6.

`secure contoso` shows the oversharing guarantee: a restricted user grounds on
fewer records and gets a different, less-alarming answer, because the column can
only use what that user may read.

## How it maps to the proposal

| Part of this prototype | Proposed native feature |
| --- | --- |
| `ground()` security-trimmed retrieval | **F1** grounding as a knowledge source |
| `_Sources` citation payload (`citations.py`) | **F2** persisted citations |
| `refresh.incremental_refresh` + reverse index | **F3** backfill and incremental refresh |
| `cost.py` estimate and budget cap in `enrich_view` | **F5** cost transparency and budget |
| `RESTRICTED` principal in `secure` | oversharing guardrail |

## Live mode (against a real Dataverse org)

Live mode swaps mock data for real Dataverse retrieval and calls the actual AI
Builder prompt via the `Predict` message.

```bash
pip install azure-identity
az login                                   # or an interactive browser sign-in
export DATAVERSE_URL="https://YOURORG.crm.dynamics.com"
export PROMPT_MODEL_NAME="Renewal Risk Summary"
# then run the live path (see examples/ and src/gpc/client.py)
```

Prerequisites in the org: a Dataverse database, the Copilot / AI Prompts feature
on, and a licensed maker account. The `Predict` payload shape is isolated in
`client.py` so it is the only place to validate against your org.

## Project layout

```
cli.py                 command-line demo
src/gpc/
  mockdata.py          sample Dynamics 365 Sales data (mock mode)
  ground.py            F1: security-trimmed retrieval + fingerprint
  generate.py          baseline vs grounded generation (mock + live)
  citations.py         F2: persisted sources + reverse index
  cost.py              F5: credit estimation
  enrich.py            orchestrator + backfill + budget cap
  refresh.py           F3: incremental, change-only refresh
  client.py            live Dataverse client (Predict, query, update)
  config.py            live-mode config
examples/
  grounded_prompt_column.py
```

## Status

Prototype. Mock mode is fully runnable today. Live mode is wired against public
APIs and is validated per environment. See the companion product one-pager and
execution plan for the full proposal.
