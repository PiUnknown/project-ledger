# Decisions

Format and lock protocol are defined in AGENTS.md. Append-only for the log. Proposals become decisions only when the maintainer approves them, recorded here with the date.

## Decided (maintainer brief and plan, 2026-11-18)

- D-001 Fixed stack: Next.js, FastAPI, LangGraph, OpenAI models, hosted Postgres. LangSmith tracing recommended.
- D-002 Three roles with a demo toggle: owner, inventory_manager, purchase_manager. The toggle is not authentication.
- D-003 Read-only Q&A is the baseline. Writes are a bonus, local private deployment only, with exact-change confirmation, built last.
- D-004 Answers must be evidence-backed from the database only. When the data cannot answer, say so.
- D-005 The agent decides whether to present text, a table or a chart.
- D-006 The supplied database is never modified. Schema inspection is read-only and its notes stay local.
- D-007 Development uses the maintainer's private full copy. The public demo uses a fabricated dataset only.
- D-008 LangSmith tracing stays off until the maintainer decides what may be disclosed to it.
- D-009 Role enforcement sits in front of the model, deny-by-default including aggregates, joins and derived values, with no arbitrary model-written SQL. The guard node is defense in depth only.
- D-010 Per-role conversation isolation.
- D-011 Inventory manager must never see prices, including indirectly.
- D-012 Documentation authority map as stated in AGENTS.md.
- D-013 Maintenance rule: ChangeLog.md, Decisions.md and Flow.md are updated after every code edit under the `.doclock` protocol in AGENTS.md.

## Proposals (not decided)

Each lists a default used so work can proceed, and what approval changes.

- P-001 Postgres roles plus per-role views, with model-written SQL over views only. Default until decided: typed tools behind the RoleExecutor interface. Approval would amend D-009. Depends on schema classification and on whether roles and views can be created on the private copy and the hosted demo database.
- P-002 A single RoleExecutor interface with a mock implementation first. Default: yes, because it lets lanes work in parallel.
- P-003 Purchase manager limits. Default until decided: role is not configured and returns `role_not_configured`. Suggested starting point for the maintainer to accept or change: sees cost price, supplier and stock data and sales volume, but not selling price, margin or revenue. Whether this works depends on whether the schema separates cost from selling price.
- P-004 The model chooses the presentation type and column mapping. The server builds the table or chart payload from the executed rows, so charts cannot show invented numbers.
- P-005 An evidence panel showing the role-visible query or tool call and a preview of the rows behind each answer.
- P-006 Guard design: structural checks at runtime (forbidden field names and monetary patterns), value-based checks in evals against the known dataset.
- P-007 Hosting: frontend, backend and Postgres on free tiers. Specific hosts to be chosen after verifying current limits and cold-start behavior.
- P-008 Startup guards and limits: refuse private data and writes when `APP_ENV=hosted`, per-IP rate limit, daily request cap, row cap, query timeout. The app-side guards are the enforced limits. The maintainer also configures a manual provider-side spending cap in the OpenAI dashboard; it is not app-enforced and not a guaranteed cutoff, and complements the app-side guards.
- P-009 Chart library: recharts (the maintainer's stated default, still open).
- P-010 Relative dates ("last month") anchor to the latest date in the data. Depends on the schema.
- P-011 Whether the schema structure may appear in the public repo through the fabricated dataset. Needs a check against the case brief. Until decided, schema notes stay in docs/schema.local.md and the seed generator is not published with real structure.
- P-012 Python dependency files as `requirements.txt` and `requirements-dev.txt`. Default: yes.

## Implementation decision log

Append entries below.

### 2026-11-18 | Planning
No decision changed beyond those listed above.

### 2026-11-18 | Planning
No decision changed.