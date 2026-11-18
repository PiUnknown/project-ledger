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

### 2026-11-18 | Lane 0
No decision changed.

### 2026-11-18 | Lane 0 | lane0-c4b2
Decision: Created backend/requirements.txt with fastapi, uvicorn, langgraph, langchain-openai and backend/requirements-dev.txt with pytest, ruff. Package names derived only from PROJECT_SPEC.md (FastAPI, LangGraph, OpenAI), README.md Running section (uvicorn), and README.md Testing section (pytest, ruff). No version pins because the documents do not state any. langchain-openai is included as the standard LangChain integration package for OpenAI models used through LangGraph.
Rationale: README Setup step 3 expects these files to exist. Lane 0 owns tooling config per docs/ownership.md. P-012 proposes this naming convention as the default. Creating the files completes the scaffold to match what README Setup documents.
Alternatives considered: Including the bare openai SDK separately; not done because langchain-openai already depends on it and the agent layer accesses models through LangGraph. Including pydantic explicitly; not done because fastapi depends on it and the documents do not name it as a separate requirement.

### 2026-11-18 | Lane 0 | lane0-c4e9
Decision: Until the maintainer resolves the three open Lane 0 change requests, follow docs/ownership.md for file-level conflicts: Lane A owns the mock executor and backend/app/enforcement/interface.py, Lane F owns CI files under .github/workflows/, and Lane 0 structural placeholders are empty-directory markers only. The explicit Lane 0 exception is frontend/.env.local.example.
Rationale: This is the requested working interpretation of the ownership precedence. It does not close the change requests, change the contract, or amend PROJECT_SPEC.md or docs/ownership.md.
Alternatives considered: Treat the broader Lane 0 scaffold goal as permission to create files in the conflicting areas; not used while the three change requests remain open.
References: Change request 1, mock executor and interface ownership; change request 2, CI ownership; change request 3, backend health route and frontend file boundaries, as recorded in the Lane 0 audit.
The CI ownership overlap and the PROJECT_SPEC.md versus docs/ownership.md conflicts recorded in ChangeLog.md remain unresolved. No lane ownership was changed.

### 2026-11-18 | Lane A | laneA-9e7d
Decision: Use a fixed, typed mock operation behind RoleExecutor and an in-process, thread-safe per-IP minute limit and UTC-day request cap. Keep application configuration in environment variables with positive defaults for limits. The chat stub recognizes only fixed sample-item commands; it never treats request text as SQL.
Rationale: These implementation choices provide a schema-independent API and safety boundary while the real schema and agent remain unavailable. The mock fixture is explicitly fabricated and does not describe database columns.
Alternatives considered: Database access and arbitrary model-provided operations were not used because schema inspection is blocked and data execution must remain role-scoped.

### 2026-11-18 | Lane A | laneA-9e7d
No decision changed.

### 2026-11-18 | Lane A | laneA-9e7d
Decision: The RoleExecutor call receives the configured row limit and query timeout budget.
Rationale: The executor is the boundary that can enforce both limits on data operations, including when a future implementation uses a database.
Alternatives considered: Keeping the timeout only in API error mapping would not let an executor apply it to an operation.

### 2026-11-18 | Lane D | laneD-a31f
Decision: Store the schema-independent role policy as JSON and make query validation consume classifications rather than field names. Keep the seed generator callback-based and independent of any row structure.
Rationale: JSON uses the standard library, while the column mapping and fabricated dataset structure are unavailable before gate G1. The validator denies restricted-role classifications that are missing or unresolved.
Alternatives considered: YAML would add a dependency. Defining database fields or seed row models before schema inspection would invent structure.

### 2026-11-18 | Lane D | laneD-a31f
No decision changed.

### 2026-11-18 | Lane F | laneF-b81c
Decision: The backend CI workflow runs on push and on pull_request, on the GitHub-hosted ubuntu-latest runner, using actions/checkout@v7 and actions/setup-python@v7. It installs both backend requirement files with `python -m pip install --no-cache-dir` and runs `python -m ruff check . --no-cache` and `python -m pytest -p no:cacheprovider` with working directory backend/. The workflow token permission is contents read. The trigger key is quoted. Pip cache and action dependency cache stay off. Proposal P-007 is unchanged. No publishing config was added.
Rationale: The task requires Python 3.12, those two requirement files, and those two cache-disabled checks from backend/. ubuntu-latest is the Actions runner, not a demo host. checkout and setup-python v7 are the current major versions as of 2026-11-18. `python -m` binds the checks to the interpreter that received the install. Quoting the trigger key keeps a YAML 1.1 parser from reading it as a boolean. Contents read is enough to check out the repo and run the checks.
Alternatives considered: checkout v4 and setup-python v5 were not used because the current majors are v7 and the older majors target a retired Node runtime. A demo host and a publishing workflow were not added because that work waits for the later integration steps. The full local pytest suite was not run during parallel lane work.

### 2026-11-18 | Lane C | laneC-4f2b
Decision: The frontend is Next.js 16 with the App Router and TypeScript, with one client component tree under `components/` and one module per contract concern under `lib/`. Data access goes through a single `ChatClient` interface in `frontend/lib/api.ts`, with an `HttpChatClient` used when `NEXT_PUBLIC_API_BASE_URL` is set and a `FixtureChatClient` used otherwise. Components never call `fetch` or import a transport directly. `frontend/lib/types.ts` mirrors docs/api.md contract 0.1 and is never versioned by this lane.
Rationale: A single interface keeps every renderer independent of where a response came from, so replacing the placeholder fixtures with Lane A's contract fixtures, or with the live backend, changes no component. The frontend stays a pure renderer of the contract, which is what docs/roles.md requires when it puts enforcement on the server. docs/ownership.md requires `frontend/lib/types.ts` to mirror docs/api.md, and only Lane A may freeze or version the contract.
Alternatives considered: Server components fetching the API directly were not used, because the role toggle, thread id and evidence selection are client state. A state library was not added, because the app has one screen and React state is enough. Passing a backend base URL through a `NEXT_PUBLIC_` variable beyond the documented one was not done; the frontend reads only `NEXT_PUBLIC_API_BASE_URL`.

### 2026-11-18 | Lane C | laneC-4f2b
Decision: Dependencies added to `frontend/package.json`. Runtime: `next`, `react`, `react-dom`, and `recharts` for chart rendering under proposal P-009. Development: `typescript`, `@types/node`, `@types/react`, `@types/react-dom`, `eslint`, `eslint-config-next`, `vitest`, `@vitejs/plugin-react`, `jsdom`, `@testing-library/react`, `@testing-library/jest-dom`, and `@testing-library/user-event`. No dependency was added for state management, styling, dates or HTTP; the platform covers those.
Rationale: AGENTS.md allows a dependency when it is needed and recorded here. Next, React and TypeScript are the fixed stack in D-001 and the task. Recharts is the maintainer's stated default for charts in P-009, and P-004 requires charts to be built from executed rows, which recharts does without inventing values. Vitest with jsdom and Testing Library is the smallest setup that renders React components and asserts on rendered contract text. `eslint-config-next` brings the flat config the project lints with. No secrets or telemetry packages were added and telemetry stays disabled through `NEXT_TELEMETRY_DISABLED` when commands run.
Alternatives considered: A CSS framework was not added; the Figma export's styling was adapted into plain CSS in `frontend/app/globals.css`, which keeps the dependency list short. A separate chart library such as Chart.js was not added, because P-009 names recharts. Jest was not used, because Vitest runs TypeScript and JSX without a separate transform setup and needs no Babel config.

### 2026-11-18 | Lane C | laneC-4f2b
Decision: Placeholder fixtures live in `frontend/lib/fixtures.ts` and are labelled `PLACEHOLDER - REPLACE WITH CONTRACT FIXTURES AT INTEGRATION`. They cover all five statuses, all five non-null reason codes, and all three presentation types, and they contain no monetary value, no table name and no column name, because docs/schema.local.md does not exist. While they are in use, the sidebar exposes one entry per fixture so each status can be previewed, and a submitted message returns the documented `role_not_configured` refusal for `purchase_manager` and one deterministic answer otherwise. `resolvePlaceholderResponse` is the only place that special-cases a role, and it does so only to return the refusal docs/roles.md already defines.
Rationale: Lane A's contract fixtures do not exist yet, and AGENTS.md forbids inventing schema names or business facts. Keeping every value in one clearly marked file means the integration step deletes one file's contents instead of editing components. Preview entries let the reviewer see every status without the UI pretending to understand language. Omitting monetary values means the inventory manager fixtures cannot leak price information even by accident.
Alternatives considered: Rendering the Figma export's fabricated answers was rejected, because those answers and its refusal logic are invented content. Guessing which message should produce which status was rejected, because that would put fake natural language behaviour in the UI. Hiding statuses behind a query parameter was rejected in favour of a visible, labelled list.

### 2026-11-18 | Lane C | laneC-4f2b
Decision: Fonts come from `next/font/google` (DM Sans for body text and Manrope for display), which are downloaded at build time and served from the application origin. The client thread id is created on role switch and on a new conversation, and on the first message of a fresh page load rather than in a mount effect. `frontend/vitest.config.mts` uses a 20 second test and hook timeout.
Rationale: `next/font/google` self-hosts the font files, so the browser makes no third party request at runtime and no new external service is used. Creating the thread id in a mount effect tripped the `react-hooks/set-state-in-effect` rule and caused a second render for no benefit, so the id is created when it is first needed, and every path that must reset it does so explicitly. The longer timeout exists because other lanes build in this same folder, and jsdom plus userEvent were exceeding the 5 second default and reporting false failures.
Alternatives considered: Keeping the Figma export's `@import` from `fonts.googleapis.com` was rejected, because it is a runtime third party request and adds an external dependency. A system font stack was kept as the fallback in CSS in case the build time font fetch is unavailable. Initialising the thread id at module scope was rejected, because it would be evaluated on the server as well and could differ between server and client markup.

### 2026-11-18 | Lane C | laneC-4f2b
Decision: This session's maintainer instruction is recorded here, as AGENTS.md requires. The instruction was that Lane C initializes the Next.js and TypeScript app inside `frontend/` itself, that Lane 0 creates only the empty folder layout, that `npm install` runs only inside `frontend/`, and that the Figma Make export is visual reference only and must not contribute its fabricated answers or refusal logic. This session therefore created the frontend application files and the frontend tooling configuration, and added the frontend dependencies to `frontend/package.json`, which docs/ownership.md makes append-only for a lane adding a dependency its own code needs.
Rationale: docs/ownership.md line 27 assigns `frontend/` to Lane C, and docs/ownership.md line 17 makes `frontend/package.json` append-only for this purpose. Line 16 assigns tooling config to Lane 0 and then Lane F, which overlaps an application that must build itself, so this entry records that the session instruction is the basis for the frontend tooling files. The overlap is reported to the maintainer as a change request and is not resolved here.
Alternatives considered: Waiting for Lane 0 to create the tooling files was not possible, because the instruction assigns frontend initialization to this lane and the app cannot build without a TypeScript and Next config. Editing tooling config outside `frontend/` was not done.

### 2026-11-18 | Lane A | laneA-d241
No decision changed.



### 2026-11-18 | Lane D | laneD-e784
No decision changed.

### 2026-11-18 | Lane C | laneC-4b1e
Decision: The frontend fixtures are a transcription of Lane A's frozen contract, not hand-written example data. `buildContractFixtures()` loops over the same five statuses and three presentations as `backend/tests/api/contract_fixtures.py`, and `tests/contract-fixture-parity.test.ts` asserts the 15 objects equal `tests/contract-fixtures.snapshot.json`, which was generated from the Python source rather than typed by hand. The fixture client mirrors `backend/app/api/agent_stub.py`: `purchase_manager` returns `role_not_configured`, the three fixed demo commands return the mock table from `mock_items.json`, and every other message returns the clarification text. Export names changed from placeholder names to contract names at the two import sites only. Fixture previews keep `role: "owner"` exactly as the frozen responses carry it, so no fixture is doctored to match the active role.
Rationale: AGENTS.md forbids inventing schema names or business facts, and the maintainer instruction was to use Lane A's fixtures verbatim without adapting the contract to the UI. Generating the snapshot from the Python source makes drift detectable instead of a matter of review. Mirroring the stub in the fixture client keeps the UI's live path behaviourally identical to the current backend rather than presenting invented answers. Keeping `role: "owner"` means the UI only renders what a response carries.
Alternatives considered: Hand-writing the 15 responses was rejected because a typo would silently diverge from the frozen contract. Rendering fixtures under the active role was rejected because it would alter frozen payloads to fit the UI. Adding a second mock language path in the UI was rejected because the role and intent decisions belong to the server.

### 2026-11-18 | Lane C | laneC-4b1e
Decision: Presentation corrections are derived from the payload only. Table and evidence row counts use singular or plural wording from the count, and the chart container sizes itself to the fixed 220px chart instead of clipping it, with `maxBarSize` and explicit margins keeping a single bar and its axis labels inside the card.
Rationale: Lane A's frozen fixtures contain exactly one row, which exposed a hard-coded "rows" label, and the single-bar chart exposed both an oversized bar and a clipped x-axis label. Both are renderer facts, not fixture content, so no fixture value was changed to hide them.
Alternatives considered: Changing the fixture row count was rejected because the contract is frozen. Leaving the singular label was rejected because it is visibly wrong for a one-row response.

### 2026-11-18 | Lane E | laneE-8e4a
Decision: Implemented the leak scanner as a pure, recursive function in `backend/app/guard/scanner.py` that operates on raw dictionaries or Pydantic models. It applies deny-by-default role filtering: for restricted roles (`inventory_manager`, unconfigured `purchase_manager`), it scans dictionary keys, table column keys/labels, chart x/series keys/labels, evidence columns/detail/rows, notes, and error bodies for forbidden monetary field names, currency patterns, and qualitative price words. For all roles, it scans for credential/secret patterns. The eval harness in `evals/` defines probes as tuples `(role, question, expected_status, forbidden_strings)` covering all indirect probes from `docs/roles.md`. Integration probes against the live API are routed through a single guarded entry point in `evals/runner.py` that detects API reachability and returns `NOT RUN - NO LIVE API` without error when the server is absent.
Rationale: Defense in depth requires scanning the entire response body, including evidence details and error messages, before transmission. Keeping the scanner pure and recursive avoids coupling to unfinished agent or database components. Gating the live eval runner on API availability ensures test collection and security testing run reliably in parallel development environments without network dependencies.
Alternatives considered: Raising exceptions directly on leak detection was rejected in favor of returning a structured `ScanResult` object with violation paths and messages, allowing callers (guard nodes, API middleware, and evals) to inspect and log exact leak locations. Hardcoding test secret strings in test files was rejected to prevent repository secret scanners (AT-13) from flagging test fixtures.

### 2026-11-18 | Lane A | laneA-3b72
No decision changed.
