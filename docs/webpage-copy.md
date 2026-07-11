# Grounded Prompt Columns, webpage copy deck (v1 draft)

Explainer / landing page copy for the grounded prompt columns proposal.
Value first, then what, then how, then proof. This is the words and the flow;
the page is not built yet.

---

## One-liner (the thing people should get in 3 seconds)

**Primary:**

> **Grounded prompt columns in Dataverse, powered by MCP tools.**
> Make any column agentic: it reasons over your whole Dataverse, per row, and cites its sources.

**Alternates (pick by audience):**

- "Turn a prompt column into an agent, right in the grid."
- "Your prompt column can now read your entire Dataverse, not just the row it lives in."
- "Row-level agents. No downstream plumbing."

---

## 1. Hero (lead with customer value)

**Headline:** Push the agent into the column.

**Subhead:** Today, answering a question that spans a customer's notes, emails, and pipeline means building an agent or a flow and maintaining the retrieval yourself. Now you flip one toggle on a prompt column, and the column does it: it searches and queries your Dataverse for that row, writes the answer, and shows the records it used. Your apps, views, and reports just read a field.

**The value in one breath:** The reasoning happens where the data lives. Everything downstream stays simple.

> Screenshot: the grid with a live "Renewal Risk" column populated per row.

---

## 2. What exactly is this? (the plain definition)

A prompt column is an AI Builder column that runs a prompt for every row. We are adding a **second grounding option** to it.

- **This record (Prompt Builder)** — today's behavior. The column grounds on the current row and any related tables you pre-wire. Unchanged, still the default.
- **Your Dataverse (AppIQ)** — new. The column calls the **Dataverse MCP tools** at runtime to retrieve and reason across your whole Dataverse, structured and unstructured, and cites what it used.

Opt-in. Non-breaking. Existing columns are untouched.

---

## 3. The gap today (why this doesn't already exist)

A prompt column can only see the row it runs on. That is fine for "summarize this record," but it cannot:

- **Search by meaning.** It does attribute and relationship filters, not semantic search over notes, emails, and files.
- **Query across the org.** No JOINs, no aggregates, no "look at this account's whole pipeline."
- **Decide what to fetch.** Grounding is wired at design time by the maker, not chosen at runtime by the model.

So today, the moment your answer needs more than the row, you leave the column and go build an agent or a flow. That is the gap.

> Screenshot: the "This record (Prompt Builder)" pane producing a generic, un-grounded answer.

---

## 4. What we are building (the proposal)

The same prompt column, with a grounding toggle. Choose **Your Dataverse (AppIQ)** and the column gains three capabilities Prompt Builder cannot do:

1. **Semantic search** over notes, emails, and files (`search_data`)
2. **Relational query and aggregation** across tables (`read_query`)
3. **Runtime tool-calling**, the model decides what to pull for each row (`search`, `fetch`, `describe_table`, `list_tables`)

Same output surface as before: a persisted per-row value, plus a `_Sources` citation set. Read-only. Security-trimmed to the user.

> Screenshot: the "Your Dataverse (AppIQ)" pane with the MCP tool list and the editable instruction.

---

## 5. Can Prompt Builder already do this?

**No, and here's the precise line.** Prompt Builder is not only same-row. With **Add knowledge** it can pre-wire related tables (1:N / N:1, up to 2 levels, up to 1000 rows) with attribute filters, so it does pull some related structured data. But three things are architecturally out of reach. Those three are the moat.

### The comparison

| | This record (Prompt Builder) | Dataverse tools (AppIQ, advanced) | Moat? |
|---|---|---|:---:|
| **Scope** | the current row (+ pre-wired related) | all of Dataverse (scoped, read-only) | |
| **Retrieval** | fixed, maker-configured at design time | runtime tool calls, the model decides what to fetch | ● |
| **Unstructured / semantic** | no | yes, notes / emails / files, by meaning (`search_data`) | ● |
| **Cross-record / aggregate** | no | yes, `SELECT ... JOIN ... GROUP BY` across tables (`read_query`) | ● |
| **Output** | value + citations | value + citations *(same, by design)* | |
| **Best for** | summarize / classify this record | reason across the org, with sources | |

The rows marked ● are where Prompt Builder structurally cannot follow. The **Output** row is deliberately identical: same persisted value, same `_Sources`, so nothing downstream changes.

### The moat, in three lines

1. **Runtime tool-calling, not design-time grounding.** Prompt Builder fixes the grounding when the maker builds it (these tables, this relationship, these filters). The advanced column decides at runtime what to fetch for the question in front of it. Fixed knowledge vs an agent that goes and gets what it needs.
2. **Semantic search over unstructured content.** Prompt Builder does relationship + attribute-filter retrieval. It cannot do meaning-based search over notes, emails, and attachments. `search_data` can. This is the churn-signal-in-the-notes case Prompt Builder simply cannot reach.
3. **Relational query and aggregation across the org.** Prompt Builder retrieves related records; it cannot run a query, compute across accounts, or reach arbitrary un-related tables. `read_query` / the SDK's SQL can.

**The punch line:** the moat is not *more data*, it is a *different retrieval paradigm*. Fixed, maker-wired knowledge versus a read-only agent that searches and queries all of Dataverse, structured and unstructured, and cites what it used. A paradigm difference, not a bigger knob.

### Why "advanced option, don't touch the default" is the right move

- **Non-breaking / opt-in.** Existing columns keep Prompt Builder, unchanged. Zero migration, zero risk. Teams say yes to additive far faster than to change.
- **Progressive disclosure.** Simple default for the 80% case, advanced for the power case, the pattern Microsoft already ships.
- **It isolates the scary parts.** Security, cost, latency, and governance live only in advanced mode. You are not turning every prompt column into an agent, and that isolation is itself a selling point to reviewers.
- **Technically correct, not just safe.** Advanced is agentic (tool-calling, non-deterministic, heavier), so it genuinely should not be the default. Opt-in is the right engineering call too.

### Two refinements to show it's safe

- **Scope controls on advanced mode.** The maker can limit which tables and tools it may use (for example, "search + query over Accounts, Cases, Notes"), read-only tools only. Bounds security, cost, and injection surface.
- **Same output surface.** Both modes produce the same persisted value + `_Sources` + status. Downstream apps, flows, and reports don't care which mode made the value; only the grounding differs.

---

## 6. How it works (the mechanism, honestly)

For each row, the column runs a small agent loop:

**Retrieve** (Dataverse MCP tools) -> **Reason** (the prompt) -> **Cite** (the real records).

You author a normal instruction, for example *"Write a two-sentence renewal risk summary for {Account.name}."* The `{Account.name}` token resolves to the current record; the tools do the rest and pull whatever is relevant to that question. Change the instruction and the retrieval adapts.

> Screenshot: the live answer with clickable citations, plus the expandable "How it was grounded (tool calls)" trace.

---

## 7. Why it matters (the customer value, expanded)

**Agentic at the row level means no agent downstream.** Instead of building and maintaining a separate agent, flow, or Copilot to do multi-step reasoning over Dataverse, you declare it once as a column. The complexity moves upstream into a single field; every report, view, and app downstream just reads a value like any other column.

- **Grounded** — answers come from your real records, not the model's guess.
- **Cited** — every value links back to the notes and rows it used.
- **Fresh** — it retrieves at run time, so it reflects the data as it is now.
- **Simple downstream** — the hard part is done in the column, so nothing after it needs custom processing.

**What it is not:** it is not one org-wide answer repeated on every row. Each row gets its own answer; "your Dataverse" is the grounding it retrieves from, not a shared result.

---

## 8. See it (highlight / demo strip)

A short, screenshot-led walk-through:

1. **The column in the grid** — Renewal Risk, filled per account. *(screenshot)*
2. **Edit prompt, two grounding options** — the toggle. *(screenshot)*
3. **This record vs Your Dataverse** — same account, generic answer vs grounded high-risk answer. *(side-by-side screenshot)*
4. **The tools and the trace** — which MCP tools ran, and the records cited. *(screenshot)*
5. **Semantic search proves its worth** — turn `search_data` off and the answer misses the churn signal. *(screenshot / the three-tier compare)*

---

## 9. Trust and guardrails (the safety line)

Live only in the advanced mode: **read-only tools** (no create, update, or delete), **user-scoped and security-trimmed** retrieval, maker control over which tools and tables are in scope, and a full audit of every tool call. The write and delete MCP tools are deliberately not exposed to a prompt column.

---

## 10. Close / call to action

**Keep "this record" for the simple cases. Choose "your Dataverse" when the answer lives across it.**
Opt-in, non-breaking, and your existing columns keep working exactly as they do today.

> Optional CTA: "Try the live demo" -> the deployed grid.

---

## One-line positioning (reusable)

> **Prompt columns get a second grounding option.** Keep "this record" for simple cases, or choose "Dataverse tools" to let the column search and query your entire Dataverse, structured and unstructured, with citations. Opt-in, non-breaking, existing columns untouched.

---

## Design notes (for when we build the page)

**Palette (Power Apps chrome, matches the demo):**

- Power Apps purple (brand / command-bar banner): `#742774`  (RGB 116, 39, 116)
- Ink: `#242424`   Secondary ink: `#605e5c`   Faint: `#a19f9d`
- Borders: `#edebe9` / `#e1dfdd`   Hover: `#f3f2f1`
- Semantic: good `#107c41` on `#dff6dd`; warning `#8a5a00` on `#fff4ce`; critical `#a4262c` on `#fde7e9`
- Sibling product colors (reference only): Power Automate `#0066FF`, Power BI `#F2C811`

**Type:** Segoe UI (Segoe UI Web via the Fabric CDN), with Consolas / mono for prompts and tool traces.

**Theme:** the demo styling is the source of truth (see `web/app/static/index.html` and `semantic.html`).

**Naming:** advanced grounding option / tool layer = "Dataverse AppIQ MCP Tools"; umbrella brand = "Dataverse Intelligence". Maker-facing label can stay descriptive ("Ground on your Dataverse data (advanced)").
