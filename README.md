# Factory Item Agent

A take-home case study. An AI agent answers plain-English questions about a factory's items, stock, pricing and sales, using only the factory's database. Three demo roles see different slices of the data.

Status: planning in review, no code yet. Proposals are pending maintainer approval and the schema is unknown. The supplied database returned "Connection reset", so schema inspection is pending and nothing here names real tables or columns.

## Stack (fixed by the brief)

- Frontend: Next.js
- Backend: FastAPI
- Agent: LangGraph
- Models: OpenAI
- Database: hosted Postgres
- Tracing: LangSmith (recommended, currently off by default, see Limitations)

## Roles

Roles are `owner`, `inventory_manager` and `purchase_manager`. A demo toggle in the UI switches between them. The toggle is not authentication. Details live in docs/roles.md.

## Repository layout (planned)

```
README.md  PROJECT_SPEC.md  GLOSSARY.md  AGENTS.md
ChangeLog.md  Decisions.md  Flow.md
docs/        api.md  roles.md  ownership.md  schema.local.md (local only)
backend/     .env.example  pyproject.toml  app/ and tests/ added by owning lanes
frontend/    .env.local.example  Next.js app added by Lane C
db/          policy, views, seed, migrations
evals/       cases and runner
```

The scaffold starts with the documented project and environment files. Each lane adds implementation files only in its owned directories. `docs/schema.local.md` is local only and stays gitignored.

## Prerequisites

- Python 3.12 or newer
- Node.js current LTS (22 or newer)
- Postgres 15 or newer, local or hosted
- An OpenAI API key with a spend cap configured manually by the maintainer in the OpenAI dashboard. This is a manual provider-side setting, not app-enforced and not a guaranteed cutoff. The app-side guards (per-IP rate limit, daily request cap, row cap, query timeout, hosted-mode startup refusals) are the enforced limits; the dashboard setting complements them.

## Local setup

Run these commands from the repository root in Windows PowerShell. Each command is on its own line.

1. Environment setup:
   ```powershell
   Copy-Item backend/.env.example backend/.env
   Copy-Item frontend/.env.local.example frontend/.env.local
   ```
   - The frontend never receives `DATABASE_URL`, any `DATABASE_URL_*` variant, `OPENAI_API_KEY`, or any secret.
   - Fill values yourself. Never commit secret env files. The scaffold lane must ignore secret env files and `.doclock` in `.gitignore` while preserving env example files.
2. Backend:
   ```powershell
   Set-Location backend
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt -r requirements-dev.txt
   Set-Location ..
   ```
3. Frontend:
   ```powershell
   Set-Location frontend
   npm install
   Set-Location ..
   ```
4. Database: see "Private copy of the database" below, or load the fabricated dataset with the seed script once it exists (`python -m db.seed`).

## Environment variables (names only)

Documented in `backend/.env.example` (backend and shared variable names, empty values):

- `APP_ENV`: `local` or `hosted`
- `DATA_PROFILE`: `private` or `fabricated`
- `DATABASE_URL`: read-only connection string for the baseline executor
- `DATABASE_URL_OWNER`, `DATABASE_URL_INVENTORY`, `DATABASE_URL_PURCHASE`: used only if proposal P-001 is approved
- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `LANGSMITH_TRACING` (default `false`), `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT`
- `CORS_ALLOWED_ORIGINS`
- `RATE_LIMIT_PER_MINUTE`
- `DAILY_REQUEST_CAP`
- `QUERY_ROW_LIMIT`
- `QUERY_TIMEOUT_MS`
- `WRITES_ENABLED` (default `false`)

Documented in `frontend/.env.local.example` (only `NEXT_PUBLIC_API_BASE_URL`):

- `NEXT_PUBLIC_API_BASE_URL`

The frontend never receives `DATABASE_URL`, any `DATABASE_URL_*` variant, `OPENAI_API_KEY`, or any secret. Never put a secret in a `NEXT_PUBLIC_` variable.

Evals: `EVAL_API_BASE_URL`.

Maintainer only: `SOURCE_DATABASE_URL`, used by hand for the one-time copy below. The app and the coding agents never use it.

## Private copy of the database (maintainer only)

The supplied database is never modified and never touched by coding agents.

1. Obtain read-only credentials from the case provider.
2. Copy it into your own Postgres:
   - `pg_dump --no-owner --no-privileges "$SOURCE_DATABASE_URL" -Fc -f private_copy.dump`
   - `pg_restore --no-owner -d "$DATABASE_URL" private_copy.dump`
3. Dump files are gitignored. Keep them out of the repo.
4. Write your schema notes to `docs/schema.local.md` (gitignored).

If you get "Connection reset", try in order: add `sslmode=require`, try the direct port instead of the pooled port, check for an IP allowlist, try another network. If it still fails, ask the case provider for a dump file or a schema export.

## Running

From the repository root in Windows PowerShell, start the backend:

```powershell
Set-Location backend
python -m uvicorn app.main:app --reload
```

In a second PowerShell window, start the frontend:

```powershell
Set-Location frontend
npm run dev
```

Open the frontend URL and pick a role with the toggle.

## Frontend

The app is Next.js with TypeScript in `frontend/`. It renders exactly what the response contains: the answer text, a text, table or chart presentation, the evidence panel, and the status with its reason code. It has no role rules of its own. Refusals and errors show the text the response carries.

Current state: Lane A's contract fixtures do not exist yet, so the UI runs on placeholder fixtures in `frontend/lib/fixtures.ts`. They mirror the response shapes in docs/api.md version 0.1 and cover every status, every reason code and all three presentation types. The file is marked `PLACEHOLDER - REPLACE WITH CONTRACT FIXTURES AT INTEGRATION`. While they are in use the sidebar lists one entry per placeholder scenario, so each status can be previewed without faking language understanding. A banner in the header says `PLACEHOLDER FIXTURES`.

Two data paths share one interface in `frontend/lib/api.ts`. When `NEXT_PUBLIC_API_BASE_URL` is set the UI calls the backend contract. When it is empty the UI uses the placeholder fixtures. Components never call a transport directly.

Commands, from `frontend/`:

```powershell
npm run dev
npm run build
npm run lint
npm run typecheck
npm test
```

Environment: copy `frontend/.env.local.example` to `frontend/.env.local` and set `NEXT_PUBLIC_API_BASE_URL` to the backend origin. That variable is the only one the frontend reads. No secret belongs in a `NEXT_PUBLIC_` variable, because everything with that prefix is shipped to the browser.

The role toggle starts a new thread id and clears the visible conversation when the role changes, so history never mixes roles. It is a demo control, not authentication, and the UI says so.

## Testing

- Backend: `cd backend && pytest` and `ruff check .`
- Frontend: `cd frontend && npm run lint && npm run typecheck && npm test`
- Evals (role and leak checks against a running API): `python -m evals.run_evals --role all`

## Deployment (proposal, not yet decided)

Frontend and backend on free hosting, database on a free hosted Postgres tier, public demo on the fabricated dataset only. Host choices and their free-tier limits and cold-start behavior must be verified before committing. See Decisions.md.

## Current limitations

- The role toggle is not authentication. Anyone can send any role to the API. This is why the public demo uses fabricated data only.
- Database schema is unknown until inspection succeeds. Concrete mapping is blocked.
- Purchase manager limits are not defined yet. Until they are, that role returns `role_not_configured`.
- Read-only Q&A is the baseline. Writes are a bonus and, if built, run only in a local private deployment.
- LangSmith tracing is off until the maintainer decides what may be disclosed to it.
- Free hosting may sleep when idle, so the first request can be slow.

## Documentation map

See the authority table in AGENTS.md. Start with PROJECT_SPEC.md for scope and AGENTS.md for working rules.
