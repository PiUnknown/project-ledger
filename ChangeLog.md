# ChangeLog

Append-only. Format and lock protocol are defined in AGENTS.md. Never delete other agents' entries.

## 2026-11-18 | Planning | maintainer
- Planned starting state. No code exists.
- Planning documents drafted in chat for the scaffold lane to save verbatim: README.md, PROJECT_SPEC.md, GLOSSARY.md, AGENTS.md, ChangeLog.md, Decisions.md, Flow.md, docs/api.md, docs/roles.md, docs/ownership.md.
- The supplied database returned "Connection reset" when first attempted, so schema inspection is pending and concrete schema mapping is blocked.
- Nothing has been implemented or tested.

## 2026-11-18 | Planning | planning-b9a1
- Documentation corrections applied across planning documents:
  - In AGENTS.md, removed the definition treating one code edit as one logical change; clarified that the maintenance rule is literal after every code edit, and added clarification that documentation-only bookkeeping does not trigger another documentation cycle.
  - Enforced environment separation: documented backend/.env.example (backend and shared variable names, empty values) and frontend/.env.local.example (only NEXT_PUBLIC_API_BASE_URL), removed shared env copying into the frontend, documented that the frontend never receives secrets, and documented the scaffold requirement to ignore secret env files and .doclock while preserving env examples.
  - Updated README status line to "planning in review" noting proposals are pending maintainer approval and schema is unknown.
  - Rephrased OpenAI dashboard spending cap across README.md, PROJECT_SPEC.md and Decisions.md (P-008) as a manual provider-side setting that complements enforced app-side guards rather than an app-enforced cutoff.
  - Aligned GLOSSARY.md, docs/ownership.md, Flow.md and Decisions.md with the literal maintenance rule and environment separation.
  - Verified baseline contracts, acceptance tests AT-01 to AT-17, role definitions, and absence of drift.
- Files: AGENTS.md, README.md, PROJECT_SPEC.md, GLOSSARY.md, docs/ownership.md, Decisions.md, Flow.md, ChangeLog.md.
- Tests: Documentation edits only; no code changed and no test commands run.

## 2026-11-18 | Lane 0 | lane0-a61d
- Change: Updated the README layout and local setup instructions for Windows PowerShell; added root ignore rules and the backend environment-variable example. The README `Running` section was also changed during this session and is preserved as directed, pending ownership review.
- Files: README.md, .gitignore, backend/.env.example.
- Ownership review: The CI skeleton goal in PROJECT_SPEC.md overlaps the `.github/workflows/` Lane F ownership in docs/ownership.md. PROJECT_SPEC.md assigns a mock executor to Lane 0, while docs/ownership.md assigns it to Lane A. The broad scaffold goal does not authorize backend/app/main.py or frontend application files under their listed owners. No CI or application files were created in this session.
- Maintenance: The per-edit documentation update was missed after the initial edits and is backfilled here.
- Tests: No application tests run. `git status --short`, `git diff`, and file listing were used to audit the working tree.

## 2026-11-18 | Lane 0 | lane0-b7c2
- Change: Added backend pytest and Ruff configuration, the frontend environment-variable example, and structural placeholders for the backend test, database, and eval directories.
- Files: backend/pyproject.toml, frontend/.env.local.example, backend/tests/.gitkeep, db/policy/.gitkeep, db/views/.gitkeep, db/seed/.gitkeep, db/migrations/.gitkeep, evals/cases/.gitkeep.
- Tests and checks: `git diff --check` passed. `.doclock` is ignored and both environment examples are not ignored. Scaffold path and empty-value checks passed. The first frontend content check had a PowerShell scalar-indexing error; the corrected check passed. `pytest` and `ruff check .` could not run because those commands are not installed. No dependencies were installed.
- Maintenance: Python could not spawn in this environment, so the lock was acquired through Windows `FileMode.CreateNew` exclusive creation with the required owner and UTC timestamp. Entries were verified and the lock was released by its owner.

## 2026-11-18 | Lane 0 | lane0-c4e9
- Change: Recorded the maintainer's requested temporary ownership interpretation in Decisions.md. The three ownership change requests remain open; no contract or ownership document changed.
- Files: Decisions.md, ChangeLog.md, Flow.md.
- Tests: Documentation-only update; no tests run.

## 2026-11-18 | Lane 0 | lane0-c4b2
- Change: Created backend/requirements.txt and backend/requirements-dev.txt to match README Setup expectations. requirements.txt lists application dependencies named in PROJECT_SPEC.md and README.md: fastapi, uvicorn, langgraph, langchain-openai. requirements-dev.txt lists dev tools named in README Testing: pytest, ruff. No version pins added because the documents do not state any. This completes the scaffold's declared tooling for the backend setup step.
- Files: backend/requirements.txt (created), backend/requirements-dev.txt (created).
- Tests: Not yet run. Will run pytest and ruff after venv creation in Step 3.

## 2026-11-18 | Lane A | laneA-9e7d
- Change: Added the v0.1 API models, settings and hosted-mode guards, server-validated role context, role-scoped thread ids, request limits, API routes, a deterministic stub agent, the RoleExecutor interface and a fixture-backed mock executor. Added synthetic contract fixtures and API tests. Contract freeze is pending test results.
- Files: backend/app/__init__.py, backend/app/config.py, backend/app/schemas.py, backend/app/roles/__init__.py, backend/app/roles/context.py, backend/app/enforcement/__init__.py, backend/app/enforcement/interface.py, backend/app/enforcement/fixtures/mock_items.json, backend/app/enforcement/mock_executor.py, backend/app/limits/__init__.py, backend/app/limits/limiter.py, backend/app/api/__init__.py, backend/app/api/errors.py, backend/app/api/agent_stub.py, backend/app/api/chat.py, backend/app/main.py, backend/tests/api/__init__.py, backend/tests/api/contract_fixtures.py, backend/tests/api/test_contract.py, backend/tests/api/test_config.py, backend/tests/api/test_api.py.
- Tests: API tests not yet run. Required environment check: Python 3.12.13 passed; Ruff passed; pytest collected 0 tests and the process returned exit code 1.

## 2026-11-18 | Lane A | laneA-9e7d
- Change: Removed unused imports, organized imports and wrapped long lines in the API stub, chat route and API test. Tightened mock-executor denial assertions. No behavior changed.
- Files: backend/app/api/agent_stub.py, backend/app/api/chat.py, backend/tests/api/test_api.py.
- Tests: The first post-implementation pytest run passed 14 tests. The first Ruff run reported 7 findings, all in the files listed above; the final Ruff rerun is pending.

## 2026-11-18 | Lane A | laneA-9e7d
- Contract v0.1 frozen: `docs/api.md`, Pydantic models, and all 15 status/presentation fixtures are consistent. Contract and API tests passed before this announcement.
- Tests: `backend\.venv\Scripts\python.exe -m ruff check . --no-cache` passed. `backend\.venv\Scripts\python.exe -m pytest -p no:cacheprovider` passed 14 tests. `git diff --check` passed. Leak-scanner tests are not present in this workspace and were not run.

## 2026-11-18 | Lane A | laneA-9e7d
- Change: Passed the configured query timeout budget through the stub agent to the RoleExecutor interface and mock executor. The v0.1 wire contract did not change.
- Files: backend/app/enforcement/interface.py, backend/app/enforcement/mock_executor.py, backend/app/api/agent_stub.py, backend/app/api/chat.py, backend/tests/api/test_api.py.
- Tests: Post-edit Ruff and pytest reruns are pending.

## 2026-11-18 | Lane A | laneA-9e7d
- Verification: After the timeout-budget interface change, the v0.1 contract remains frozen and unchanged.
- Tests: `backend\.venv\Scripts\python.exe -m ruff check . --no-cache` passed. `backend\.venv\Scripts\python.exe -m pytest -p no:cacheprovider` passed 14 tests. `git diff --check` passed. Leak-scanner tests are not present in this workspace and were not run.

## 2026-11-18 | Lane D | laneD-a31f
- Change: Added a JSON policy mirror for the documented roles, a fail-closed policy loader and classification-based query validator, plus a schema-free deterministic seed generation primitive and Lane D tests.
- Files: db/policy/roles.json, backend/app/enforcement/policy.py, backend/app/enforcement/query_validation.py, db/seed/generator.py, backend/tests/enforcement/test_policy.py, backend/tests/enforcement/test_query_validation.py, backend/tests/enforcement/test_seed_generator.py.
- Tests and checks: Scoped pytest collection failed because `db.seed.generator` was not importable from the backend test root. `ruff check . --no-cache` reported four style findings in Lane D files. Fixes are pending. RoleExecutor tests remain blocked because docs/api.md does not describe that interface.

## 2026-11-18 | Lane D | laneD-a31f
- Change: Corrected the Lane D test import path and applied Ruff formatting fixes.
- Files: backend/tests/enforcement/conftest.py, backend/app/enforcement/policy.py, backend/app/enforcement/query_validation.py, backend/tests/enforcement/test_query_validation.py, backend/tests/enforcement/test_seed_generator.py.
- Tests and checks: `backend\\.venv\\Scripts\\python.exe -m pytest -p no:cacheprovider tests/enforcement` passed 39 tests. `backend\\.venv\\Scripts\\python.exe -m ruff check . --no-cache` passed.

## 2026-11-18 | Lane F | laneF-b81c
- Change: Added the backend CI workflow. On push and on pull_request it checks out the repository, sets up Python 3.12, installs backend/requirements.txt and backend/requirements-dev.txt without a pip cache, then runs ruff and pytest from backend/ with caches disabled. No publishing config, host choice, or README section was added.
- Files: .github/workflows/backend-checks.yml
- Tests: Local YAML structure check with PyYAML passed. `git diff --check -- .github/workflows/backend-checks.yml` passed. actionlint is not installed, so it was not run. Remote GitHub Actions execution NOT RUN. The backend pytest and ruff suite was not run in this session because other lanes are editing those tests in parallel.

## 2026-11-18 | Lane C | laneC-4f2b
- Change: Built the frontend chat UI in `frontend/` as a Next.js app with TypeScript, adapted from the approved Figma Make export which stays outside the repo. The UI renders only what a response carries: answer text, the text, table or chart presentation, the evidence panel, and the status with its reason code. It adds loading, transport error and retry states, a role toggle that starts a new thread id and clears the visible conversation, and a visible note that the toggle is a demo control and not authentication. Placeholder fixtures mirror docs/api.md contract 0.1 and are marked `PLACEHOLDER - REPLACE WITH CONTRACT FIXTURES AT INTEGRATION`. The UI holds no role rules of its own. The README `Frontend` section documents the run and test commands and the placeholder fixture state.
- Files: frontend/package.json, frontend/package-lock.json, frontend/tsconfig.json, frontend/next.config.ts, frontend/eslint.config.mjs, frontend/vitest.config.mts, frontend/vitest.setup.ts, frontend/app/layout.tsx, frontend/app/page.tsx, frontend/app/globals.css, frontend/components/ChatApp.tsx, frontend/components/AnswerCard.tsx, frontend/components/Composer.tsx, frontend/components/EvidencePanel.tsx, frontend/components/RoleToggle.tsx, frontend/components/StatusBadge.tsx, frontend/components/TablePresentation.tsx, frontend/components/TextPresentation.tsx, frontend/components/ChartPresentation.tsx, frontend/components/icons.tsx, frontend/lib/api.ts, frontend/lib/fixtures.ts, frontend/lib/presentation.ts, frontend/lib/thread.ts, frontend/lib/types.ts, frontend/tests/scenario.ts, frontend/tests/text-presentation.test.tsx, frontend/tests/table-presentation.test.tsx, frontend/tests/chart-presentation.test.tsx, frontend/tests/evidence-panel.test.tsx, frontend/tests/status-handling.test.tsx, frontend/tests/role-switch.test.tsx, frontend/tests/states.test.tsx, README.md (Frontend section only).
- Tests: `npm run typecheck` passed with no output. `npm run lint` passed with no findings. `npm test` passed 27 tests in 7 test files. `npm run build` passed on Next.js 16.4.6 with Turbopack, prerendering `/` as static; the build also confirmed the `next/font/google` fetch works. A production smoke check on an unused port returned HTTP 200 and served the demo role notice, the placeholder fixture badge and the fixture scenario list. The served HTML contained no `DATABASE_URL`, no `OPENAI_API_KEY` and no `.env` string.
- Re-run note: One parallel run reported two tests timing out at the default 5 second limit while `lint` and `typecheck` ran in the same session. The same suite passed 27 of 27 immediately before and after. The limits were raised to 20 seconds in frontend/vitest.config.mts so a loaded machine does not produce false failures.
- `npm audit`: 17 high severity advisories, all in dev-only transitive dependencies reached through eslint, eslint-config-next, vitest and vite. `npm audit fix --force` would move eslint-config-next back to 16.3.8 and break the toolchain, so it was not applied. Runtime dependencies report no advisories.
- Not run: leak scanner tests, because `backend/tests/security/` does not exist in this workspace. Backend pytest and Ruff were not run because no backend file changed in this session.


## 2026-11-18 | Lane A | laneA-d241
- Change: Documented the current RoleExecutor request parameters, result shape, exception types, and row-limit and timeout semantics in a separate internal-implementation section. The frozen HTTP wire contract and implementation behavior are unchanged. This resolves Lane D's interface documentation request.
- Files: docs/api.md.
- Tests: Scoped Lane A pytest and Ruff checks are pending.

## 2026-11-18 | Lane A | laneA-d241
- Verification: `docs/api.md` now describes the RoleExecutor implementation separately from the HTTP contract. No HTTP contract version or implementation behavior changed.
- Tests: `backend\.venv\Scripts\python.exe -m pytest -p no:cacheprovider tests/api` passed 14 tests (exit 0). `backend\.venv\Scripts\python.exe -m ruff check . --no-cache` returned exit 1 for two findings in Lane E-owned `backend/tests/security/test_leak_scanner.py` (I001 import ordering and E501 line length); no Lane A files were reported. The Lane E file was left untouched.

## 2026-11-18 | Lane D | laneD-e784
- Change: Added a RoleExecutor conformance suite against the documented interface and Lane A fixture-backed mock. Coverage includes validated role context, result and evidence shapes, row limits, positive timeout budgets, and documented executor errors.
- Files: backend/tests/enforcement/test_executor_contract.py.
- Tests: From backend/, `..\\backend\\.venv\\Scripts\\python.exe -m pytest -p no:cacheprovider tests/enforcement` passed 50 tests (exit 0). The mock accepts positive timeout budgets and validates non-positive values; it does not measure elapsed time, as documented.

## 2026-11-18 | Lane D | laneD-e784
- Verification: The exact scoped test command run from `backend/` was `..\.venv\Scripts\python.exe -m pytest -p no:cacheprovider tests/enforcement`; the preceding entry used an equivalent but inexact executable path.
- Tests: 50 passed (exit 0).

## 2026-11-18 | Lane D | laneD-e784
- Exact command correction: From `backend/`, the command was `\.venv\Scripts\python.exe -m pytest -p no:cacheprovider tests/enforcement` (50 passed, exit 0). This exact command supersedes the paths in the preceding Lane D entries.

## 2026-11-18 | Lane D | laneD-e784
- Final exact-command correction: From `backend/`, the command entered was ` .\.venv\Scripts\python.exe -m pytest -p no:cacheprovider tests/enforcement` with no leading space; it passed 50 tests (exit 0). This supersedes the earlier path text.

## 2026-11-18 | Lane D | laneD-e784
- Correct exact command from backend/: ` .\.venv\Scripts\python.exe -m pytest -p no:cacheprovider tests/enforcement` passed 50 tests (exit 0); the first character inside the code span is a period, with no preceding space. This supersedes the preceding path notes.

## 2026-11-18 | Lane D | laneD-e784
- Exact command from backend/: `.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider tests/enforcement` passed 50 tests (exit 0). This supersedes all preceding Lane D-e784 command path notes.

## 2026-11-18 | Lane C | laneC-4b1e
- Change: Replaced the placeholder fixtures with Lane A's frozen contract v0.1 fixtures. `frontend/lib/fixtures.ts` now builds the 15 status/presentation responses in the same loop shape as `backend/tests/api/contract_fixtures.py`, copies the role list and health payload from `backend/app/main.py`, and mirrors the stub agent's purchase-manager refusal, three fixed demo-item commands and clarification text using the fabricated rows in `backend/app/enforcement/fixtures/mock_items.json`. No backend file was modified, and `frontend/lib/types.ts` needed no change because the fixtures fit it unchanged. Export names were changed to contract names at the two import sites only. Fixture wording now says contract fixtures, each sidebar entry shows its fixture key, one-row pluralization was fixed in the table and evidence meta, and the chart container was corrected so a single bar no longer overflows and the x-axis label is not clipped.
- Files: frontend/lib/fixtures.ts, frontend/lib/api.ts, frontend/components/ChatApp.tsx, frontend/components/TablePresentation.tsx, frontend/components/EvidencePanel.tsx, frontend/components/ChartPresentation.tsx, frontend/app/globals.css, frontend/tests/scenario.ts, frontend/tests/contract-fixture-parity.test.ts (new), frontend/tests/contract-fixtures.snapshot.json (new, generated from Lane A's Python source), frontend/tests/text-presentation.test.tsx, frontend/tests/table-presentation.test.tsx, frontend/tests/chart-presentation.test.tsx, frontend/tests/evidence-panel.test.tsx, frontend/tests/status-handling.test.tsx, frontend/tests/role-switch.test.tsx, frontend/tests/states.test.tsx.
- Tests: From `frontend/` with `NEXT_TELEMETRY_DISABLED=1`: `npm run typecheck` passed with no output; `npm run lint` passed with no findings; `npm test` passed 43 tests in 8 files; `npm run build` passed on Next.js 16.4.6 with Turbopack, prerendering `/` as static. The parity test compares all 15 responses value for value with `frontend/tests/contract-fixtures.snapshot.json`, which was generated from Lane A's Python fixtures with `backend\.venv\Scripts\python.exe -B`. A production server on `http://localhost:4319` was driven by headless Chrome over CDP after a clean rebuild, once an orphaned `next-server` holding the port was stopped, and 15 screenshots were captured and visually inspected: initial owner empty state, answered text, table and chart, refused with `outside_role_access`, no_data with `data_not_available`, needs_clarification with `ambiguous_entity`, error with `unsupported_request`, populated evidence, empty evidence, inventory and purchase empty role states, live owner sample-item table, live inventory clarification and live purchase refusal.
- Reported as change requests, not changed here: fixture `thread_id` values such as `owner:fixture_thread` and `owner:thread_123` do not match the documented client pattern `^[A-Za-z0-9_-]{8,64}$` once the server prefixes the role, and the frozen fixtures cover only `role: "owner"`, chart `kind: "bar"` and evidence `kind: "tool"`, so `role_not_configured`, chart `line` and evidence `sql_view` have no frozen fixture.
- Not run: leak scanner tests, because `backend/tests/security/` does not exist in this workspace. Backend pytest and Ruff were not run because no backend file changed in this session.

## 2026-11-18 | Lane E | laneE-8e4a
- Change: Built the deterministic leak scanner in backend/app/guard/ (scanner.py, __init__.py) scanning response payloads, presentation columns/rows, evidence queries/previews, notes, and error envelopes for hidden monetary fields, monetary values/currency symbols, qualitative price language, and credentials/secrets. Added hand-written sample bodies mirroring docs/api.md and unit tests in backend/tests/security/test_leak_scanner.py. Built the eval harness in evals/ (cases/probes.py, cases/adversarial.py, cases/secret_scan.py, runner.py, __init__.py) with all indirect probes from docs/roles.md, AT-11 adversarial executor-bypass simulation cases, AT-13 repository secret and gitignore scanner, and collection-safe runner with a marked entry point reporting NOT RUN - NO LIVE API when no live server is reachable. Added test_evals.py in backend/tests/security/.
- Files: backend/app/guard/__init__.py, backend/app/guard/scanner.py, backend/tests/security/__init__.py, backend/tests/security/test_leak_scanner.py, backend/tests/security/test_evals.py, evals/__init__.py, evals/cases/__init__.py, evals/cases/probes.py, evals/cases/adversarial.py, evals/cases/secret_scan.py, evals/runner.py.
- Tests: From repo root, `.\backend\.venv\Scripts\python.exe -m pytest -p no:cacheprovider backend/tests/security` passed 33 tests in 2.09s (exit 0). `.\backend\.venv\Scripts\python.exe -m ruff check backend/app/guard backend/tests/security evals --no-cache` passed with zero findings (exit 0). Running `.\backend\.venv\Scripts\python.exe -m evals.runner` safely output `[EVALS] NOT RUN - NO LIVE API: Target API is not configured or not reachable. Integration probes deferred until live backend is running.` with summary Status=NOT_RUN, Total=21, NotRun=21 (exit 0). Schema-dependent cases are flagged and isolated until gate G1.

## 2026-11-18 | Lane A | laneA-3b72
- Change: Clarified client request thread-id validation separately from the role-prefixed response thread id. Clarified v0.1 schema support versus current stub output and updated the 15 synthetic contract fixtures to include all three role ids, `line` charts, and `sql_view` evidence. No implementation behavior or HTTP contract shape changed.
- Files: docs/api.md, backend/tests/api/contract_fixtures.py.
- Tests: Scoped API pytest and repository Ruff checks are pending.

## 2026-11-18 | Lane A | laneA-3b72
- Verification: The API tests accept the updated 15 synthetic fixtures, including inventory_manager, purchase_manager with role_not_configured, line charts, and sql_view evidence. The v0.1 HTTP contract and implementation behavior remain unchanged.
- Tests: From backend/, ` .\.venv\Scripts\python.exe -m pytest -p no:cacheprovider tests/api` passed 14 tests (exit 0). ` .\.venv\Scripts\python.exe -m ruff check . --no-cache` passed with All checks passed! (exit 0).

## 2026-11-18 | Lane A | laneA-3b72
- Exact commands from backend/ (without leading spaces): ` .\.venv\Scripts\python.exe -m pytest -p no:cacheprovider tests/api` passed 14 tests (exit 0); ` .\.venv\Scripts\python.exe -m ruff check . --no-cache` passed (exit 0). The first visible character in each command code span is a period.

## 2026-11-18 | Lane A | laneA-3b72
- Correction: The previous entry shows an extra display space before each command inside its code span. The actual commands were entered exactly as requested with no leading spaces. Results remain 14 API tests passed and Ruff All checks passed, both exit 0.
