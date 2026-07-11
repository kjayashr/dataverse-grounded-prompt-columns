# Architecture and design

How grounded prompt columns work, why the advanced option is a different retrieval
paradigm, and how the live demo is wired.

## The shape of the feature

A prompt column runs an AI Builder prompt on every row and writes the result to a
field. This proposal adds a **second grounding option** to that column.

```mermaid
flowchart TB
  Maker["Maker creates a column<br/>(data type = Prompt)"] --> Choose{"Choose grounding"}
  Choose -->|"default"| ThisRecord["This record (Prompt Builder)"]
  Choose -->|"advanced, opt-in"| AppIQ["Your Dataverse (AppIQ MCP tools)"]

  ThisRecord --> Out1["value + _Sources + status"]
  AppIQ --> Out2["value + _Sources + status"]

  Out1 --> Down["Apps · Views · Reports · Flows"]
  Out2 --> Down
```

The output is deliberately identical for both modes, so every downstream surface
reads the field the same way. Only the grounding differs.

## Why the advanced option is a different paradigm

Prompt Builder is not limited to a single row. With **Add knowledge** it pre-wires
related tables (a few hops, attribute filters). Three things remain out of reach, and
they are structural, not configuration.

| Capability | This record | Your Dataverse (AppIQ) |
| --- | --- | --- |
| Retrieval | fixed, chosen at design time | run-time tool calls, chosen per row |
| Unstructured / semantic | no | yes, notes and files, by meaning |
| Cross-record / aggregate | no | yes, queries and JOINs across tables |
| Output | value + citations | value + citations (identical) |

The moat is not *more data*, it is a *different way of retrieving it*: fixed,
maker-wired knowledge versus a read-only agent that searches and queries all of
Dataverse and cites what it used.

## The per-row loop (live demo)

In the demo, `web/app/promptcol.py` implements the loop. Because the trial org has
Dataverse search disabled, retrieval is emulated with a model meaning-match over the
real records; the record IDs, links, and citations are all real.

```mermaid
sequenceDiagram
  autonumber
  participant UI as Edit-prompt pop-up
  participant API as /api/promptcol/run
  participant PC as promptcol.run()
  participant LLM as Azure OpenAI (gpt-4.1)
  participant DV as Dataverse (real records)

  UI->>API: { mode: advanced, instruction, tools }
  API->>PC: resolve {Account.name} for this row
  PC->>DV: gather the row's linked records
  PC->>LLM: retrieval step, which records are relevant?
  LLM-->>PC: selected records (stands in for search_data)
  PC->>LLM: prompt column, instruction + selected grounding
  LLM-->>PC: grounded answer
  PC-->>API: answer + real citations + tool trace
  API-->>UI: render value, _Sources, "how it was grounded"
```

Turning `search_data` off in the tool selector drops the notes from the grounding,
and the answer degrades to structured-only, which demonstrates the value of semantic
search.

## Tool selection

The maker controls which MCP tools the column may call.

```mermaid
flowchart LR
  Mode{"Tool selection"} -->|"Auto (default)"| All["All read tools available;<br/>the model uses the relevant ones"]
  Mode -->|"Choose"| Pick["Maker picks a subset<br/>(e.g. search_data + read_query)"]
  All --> RO["read-only · user-scoped · audited"]
  Pick --> RO
```

Read tools: `search_data`, `search`, `read_query`, `fetch`, `describe_table`,
`list_tables`. The write and delete tools are never exposed.

## Freshness

Each value cites the records it used, so the column knows its own dependencies.

```mermaid
stateDiagram-v2
  [*] --> Computed: column runs (per row)
  Computed --> Watching: value + _Sources persisted
  Watching --> Recompute: a cited or linked record changes
  Recompute --> Watching: only affected rows recompute
  Watching --> Recompute: scheduled tick (if scheduled)
  Watching --> Recompute: always-fresh (on read)
```

Default is refresh-on-change. Always-fresh and scheduled are maker options in the
portal. Only affected rows recompute.

## Guardrails

- **Read-only.** No create, update, or delete tools on a prompt column.
- **User-scoped.** Retrieval is trimmed to what the signed-in user may read.
- **Maker-scoped.** The maker chooses which tables and tools are in play.
- **Auditable.** Every tool call is recorded.
- **Opt-in.** Existing columns keep Prompt Builder unchanged; the advanced controls
  and their concerns are isolated to the advanced mode.
