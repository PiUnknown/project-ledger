# Flow

Describes planned interactions. Nothing is implemented yet. Update only when interactions actually change. Lock protocol is in AGENTS.md.

## Request flow (planned)

1. The frontend sends POST `/api/chat` with `role`, `thread_id` and `message`.
2. The backend validates the request and role, applies the per-IP rate limit and daily cap, and builds the role context and the effective thread id.
3. The LangGraph agent runs: understand the question, plan a data request, execute it through the role executor, assemble evidence, decide the presentation, compose the answer, run the guard scan.
4. The role executor applies the role policy and limits, then reads from Postgres (private copy locally, fabricated dataset when hosted).
5. Refusals and no-data outcomes return as normal responses with a `status` field.
6. The backend returns the JSON contract defined in docs/api.md. The frontend renders text, table or chart plus the evidence panel.

```mermaid
flowchart TD
    UI["Next.js chat UI with role toggle"] -->|"POST api chat"| API["FastAPI chat route"]
    API --> VAL["Validate request and role, rate limit, daily cap"]
    VAL --> CTX["Build role context and effective thread id"]
    CTX --> U["Understand question"]
    U --> P["Plan data request"]
    P -->|"outside role access"| R["Refusal response"]
    P --> X["Execute through role executor"]
    X --> EX["Role executor: policy, limits, read-only"]
    EX --> DB[("Postgres: private copy or fabricated dataset")]
    X -->|"data cannot answer"| N["No data response"]
    X --> E["Assemble evidence"]
    E --> D["Decide presentation"]
    D --> W["Compose answer"]
    W --> G["Guard scan, deterministic"]
    G --> OUT["Response contract"]
    R --> OUT
    N --> OUT
    OUT --> API
    API -->|"JSON"| UI
```

## Maintenance flow (planned)

The maintenance rule is literal: after every code edit, ChangeLog.md, Decisions.md and Flow.md are updated under the `.doclock` protocol before the next code edit. Documentation-only bookkeeping (the ChangeLog, Decisions and Flow updates themselves, and saving the planning documents at scaffold time) does not trigger another cycle.

```mermaid
flowchart TD
    A["Every code edit finished"] --> B["Acquire doclock by exclusive create"]
    B -->|"exists"| C["Wait and retry, never overwrite or delete"]
    C -->|"about 10 minutes or looks abandoned"| H["Stop and ask the maintainer"]
    C --> B
    B -->|"acquired"| D["Re-read ChangeLog, Decisions, Flow"]
    D --> E["Append dated lane entries, update diagram only if interactions changed"]
    E --> F["Verify entries present"]
    F --> G["Release doclock if owner is me"]
    G --> I["Next code edit allowed"]
```

## Flow update log

2026-11-18 | Planning | initial planned flow recorded, no implementation
2026-11-18 | Planning | changed: maintenance diagram clarified to every code edit