# Project Spec

Authoritative for: scope, architecture overview, acceptance tests, lane goals, integration order. For wire contracts see docs/api.md. For role permissions see docs/roles.md. For file ownership see docs/ownership.md. Where this file summarizes those, they win.

## 1. Purpose and scope

An agent answers plain-English questions about items, stock, pricing and sales from one Postgres database, and only from that database. The user picks a demo role. The agent chooses whether to answer as text, table or chart.

In scope:
- Three roles with a demo toggle.
- Read-only Q&A with evidence for every answer.
- The agent decides the presentation type.
- A statement of "the database cannot answer this" instead of guessing.
- Public repo with setup docs and a hosted demo on fabricated data.

Bonus (last, only if time remains): writes through the agent, local private deployment only, with exact-change confirmation.

Out of scope: real authentication, multi-tenancy, streaming responses, data from outside the database.

## 2. Roles (summary)

`owner` sees everything. `inventory_manager` never sees prices or anything derived from them, including by ranking, filtering, aggregating or deriving. `purchase_manager` limits are defined by the maintainer and are pending. Full rules in docs/roles.md.

## 3. Architecture

Components:
- Frontend (Next.js): chat, role toggle, renderers for text, table and chart, evidence panel.
- Backend (FastAPI): request validation, role context, rate limits, chat route.
- Agent (LangGraph): understand, plan data request, execute, assemble evidence, decide presentation, compose answer, guard scan.
- Enforcement layer: the `RoleExecutor` interface and its implementations. Everything the agent learns about data passes through it.
- Guard: a deterministic scanner of the final response. Defense in depth only. It is never the primary control.
- Database: Postgres. Private copy for development. Fabricated dataset for the public demo.

Principles:
1. The role comes from a server-validated request field only. Message text never changes the role.
2. Enforcement sits in front of the model and is deny-by-default, including aggregates, joins, derived values and orderings.
3. Each role has an isolated conversation: the server forms the effective thread id from role and client thread id.
4. Numbers in an answer come from executed queries, never from model arithmetic.
5. The model chooses the presentation type and column mapping. The server builds the payload from the actual rows (proposal P-004).
6. Every answered response carries evidence built only from role-visible columns.
7. LangSmith stays off until the maintainer decides what may be disclosed.

Proposals affecting architecture (see Decisions.md, none are decided unless marked there):
- P-001 Postgres roles and per-role views with model-written SQL over views only. Default until decided: typed tools baseline behind the same interface.
- P-004 Server-built presentation payloads.
- P-005 Evidence panel contents.
- P-006 Guard design: structural checks at runtime, value-based checks in evals.
- P-007 Hosting choices.
- P-008 Startup guards and limits: app-side guards (per-IP rate limit, daily request cap, row cap, query timeout, hosted-mode startup refusals) are the enforced limits. A spending cap is a manual provider-side setting the maintainer configures in the OpenAI dashboard; it is not app-enforced and not a guaranteed cutoff, complementing the app-side guards.

## 4. API summary

POST `/api/chat`, GET `/api/roles`, GET `/api/health`. Full contract in docs/api.md. Domain outcomes (answered, refused, no_data, needs_clarification) return HTTP 200 with a `status` field. Transport problems use HTTP error codes.

## 5. Schema dependency register

Pending schema inspection. Nothing below may be implemented against real names until docs/schema.local.md exists.
- Where price, cost and sales amounts live and whether stock shares a table with price.
- Whether units sold are stored separately from amounts.
- Free-text columns that may embed prices.
- Columns that act as proxies for price (grades, tiers, bands).
- Supplier and cost fields.
- Item identifier and naming format, and fuzzy matching needs.
- Date range of the data, so relative dates anchor to the latest data date and not today.
- Whether roles and views can be created on the private copy and on the hosted demo database.
- Whether publishing the schema structure in the public repo is permitted by the case brief (proposal P-011).

## 6. Acceptance tests

Tests marked (S) depend on the schema and stay blocked until gate G1.

- AT-01 Every `/api/chat` response validates against the contract in docs/api.md.
- AT-02 An unknown role returns HTTP 422 with code `invalid_role`. Role claims written in message text change nothing.
- AT-03 (S) Owner asks a factual item or stock question and gets an answer with at least one evidence entry.
- AT-04 (S) Inventory manager asks directly for a price and gets status `refused`. The refusal offers a permitted alternative and names no hidden field.
- AT-05 (S) Inventory manager indirect probes are refused or answered without monetary information: earnings if all of an item were sold, ranking by value, filtering by price threshold, total inventory value, ABC analysis, average price per category, restock cost.
- AT-06 (S) For inventory manager, no monetary field name or value appears anywhere in the response body: answer text, presentation, evidence, notes or error bodies.
- AT-07 Switching role starts a fresh effective thread. Owner history is never visible to another role.
- AT-08 (S) A question the data cannot answer (market price, causes of a sales change) returns `no_data` with an explanation and no invented figures.
- AT-09 Time-series questions produce a chart, comparisons produce a table, single facts produce text. Chart and table rows equal the executed rows.
- AT-10 Every `answered` response has at least one evidence entry. Eval check: each number in answer text traces to returned rows.
- AT-11 With the model replaced by an adversarial stub that requests forbidden data, the executor rejects every forbidden request.
- AT-12 Row cap, query timeout, per-IP rate limit and daily cap return the documented errors.
- AT-13 A secret scan finds no credentials in the repo, history or logs. Secret env files and `.doclock` are ignored while env examples are preserved.
- AT-14 With `APP_ENV=hosted`, startup refuses `DATA_PROFILE=private` and refuses `WRITES_ENABLED=true`.
- AT-15 `purchase_manager` returns `role_not_configured` until limits are defined. After that, tests come from docs/roles.md.
- AT-16 Every merged change set has matching ChangeLog.md, Decisions.md and Flow.md entries.
- AT-17 (bonus) No write happens without an explicit confirmation showing the exact change. Writes work only locally.

## 7. Parallel work lanes

Goals only. File-level ownership is in docs/ownership.md, which wins on conflict.

- Lane 0 Scaffold (single agent, runs first): saves the planning documents verbatim, creates the skeleton, tooling, `.gitignore` (ignoring secret env files and `.doclock` while preserving env examples), `backend/.env.example`, `frontend/.env.local.example`, a mock executor, a fake LLM and CI skeleton. No product logic.
- Lane A Backend API: config, role context, chat route, contract models, limits, startup guards, the `RoleExecutor` interface, a mock executor.
- Lane B Agent: LangGraph graph, prompts, presentation decision, evidence assembly. Works against the interface and a fake LLM until the real executor lands.
- Lane C Frontend: chat UI, role toggle, text, table and chart renderers, evidence panel, built from contract fixtures.
- Lane D Data and policy: policy file, column classification proposal, enforcement implementation, views and roles if P-001 is approved, fabricated seed dataset. Schema-independent parts first, the rest at gate G1.
- Lane E Evals and security: eval cases, runner, leak scanner, adversarial tests.
- Lane F Packaging: CI, deployment config, README final pass, demo hosting.
- Lane G Bonus writes: do not start until the maintainer approves.

## 8. Integration order

1. Lane 0 merges the skeleton and the planning documents.
2. Contract freeze v0: Lane A finalizes docs/api.md, `schemas.py`, mock fixtures. Lanes B and C consume them.
3. Parallel build on mocks: A (API with mock executor), B (graph with fake LLM), C (UI on fixtures), E (runner and scanner on mock responses), D (schema-independent parts).
4. Integrate A and B end to end on the mock executor for all three roles.
5. Gate G1: the maintainer supplies docs/schema.local.md. Lane D classifies columns and the maintainer approves the classification. Lane D then builds the real executor, views if P-001, and seed data.
6. Integrate the real executor. Integrate C against the live API.
7. Lane E adversarial pass, leaks fixed by the owning lane.
8. Lane F packaging and hosted demo on fabricated data only.
9. Lane G, only if approved.

Two-day target: step 1 to 4 on day one, with the connection issue time-boxed. Steps 5 to 8 on day two.

## 9. Open proposals

Listed in Decisions.md. None may be treated as decided until the maintainer approves them there.