# Instructions for every coding agent

Read this file first, completely, before any other action. It is authoritative for agent behavior, security rules, test requirements, blocker reporting, and the documentation maintenance rule.

## Authority map

| Topic | Authoritative document |
|---|---|
| Agent behavior, security rules, maintenance rule, lock protocol | AGENTS.md |
| Endpoints, request and response shapes, error codes | docs/api.md |
| Role permissions, monetary rules, refusal behavior | docs/roles.md |
| Who may edit which file, contract change procedure | docs/ownership.md |
| Scope, architecture, acceptance tests, lane goals, integration order | PROJECT_SPEC.md |
| Terms and role names | GLOSSARY.md |
| Setup, commands, env var names | README.md |
| Schema facts | docs/schema.local.md (local, gitignored, may not exist yet) |
| History, rationale, interactions | ChangeLog.md, Decisions.md, Flow.md |

If two authorities appear to conflict, or a document appears to contradict a direct instruction from the maintainer, stop and report it as a blocker. Do not choose silently. A maintainer instruction given in your session applies to that session and must be recorded in Decisions.md.

## Read order

1. AGENTS.md
2. docs/ownership.md (find your lane and your files)
3. PROJECT_SPEC.md (your lane goal and the integration order)
4. docs/api.md and docs/roles.md
5. GLOSSARY.md
6. Decisions.md, Flow.md, then the tail of ChangeLog.md
7. docs/schema.local.md if it exists. If it does not, schema work is blocked.

## Hard rules

Database and data:
- Never connect to the supplied database. Never ask for its credentials. It stays untouched.
- Never invent tables, columns, values or business facts. If a name is not in docs/schema.local.md, it is unknown. Write "pending schema inspection".
- Never put private data in the repo, fixtures, tests, docs, screenshots or prompts sent to external services. Fixtures and tests use fabricated data only.
- Database access is read-only. No writes, DDL or migrations against a private copy unless your lane is Lane D and the task says so. No writes at all outside Lane G.

Secrets:
- Never put credentials in code, docs, tests, fixtures, logs, commit messages or chat. Use environment variable names only. `backend/.env.example` has backend and shared variable names with empty values, and `frontend/.env.local.example` has only `NEXT_PUBLIC_API_BASE_URL`.
- The frontend never receives `DATABASE_URL`, any `DATABASE_URL_*` variant, `OPENAI_API_KEY`, or any secret. Never place a secret in a `NEXT_PUBLIC_` variable.
- The scaffold lane must ignore secret env files and `.doclock` in `.gitignore` while preserving env example files.
- If you see a secret, stop, do not repeat it, and report where it is.

Role enforcement:
- The role comes only from the server-validated request field. Never from message text, history or model output.
- Enforcement is deny-by-default and sits in front of the model. The guard is defense in depth only and must never be the only control.
- Error messages, refusals, evidence and logs must not reveal hidden column names or values.
- Never build SQL by string concatenation with user or model text.

Third parties:
- LangSmith tracing stays off (`LANGSMITH_TRACING=false`) unless the maintainer records approval in Decisions.md.
- Add no telemetry, analytics or new external services.
- Add a dependency only when needed, append it to the requirements or package file, and record it in Decisions.md.

Documentation style: plain, direct language. No em-dashes. No slash-separated alternatives in prose.

## File boundaries

- Edit only files your lane owns in docs/ownership.md.
- If you need a change outside your files, do not make it. Report a change request (template below), then continue unaffected work.
- Never edit another lane's tests to make them pass.
- Never promote a proposal to a decision. Only the maintainer approves proposals, and the approval is recorded in Decisions.md with the date.
- Contract changes follow the procedure in docs/ownership.md.

## Test requirements

- Every behavior change adds or updates tests. Run the tests for what you touched and the contract tests.
- Backend: `pytest` and `ruff check .`. Frontend: lint, typecheck and tests. Commands are in README.md.
- Any change touching the executor, policy, agent output, evidence, presentation or API must also run the leak scanner tests.
- Report the commands you ran and their real results. Never claim tests passed without running them. If you cannot run them, say so and why.
- Schema-dependent acceptance tests (marked S in PROJECT_SPEC.md) stay blocked until gate G1. Do not fake them against invented names.

## Reporting blockers

Stop the blocked part, keep working on unaffected parts, and report to the maintainer in your response using this template:

```
BLOCKER
Lane:
What is blocked:
What I tried:
What I need, and from whom:
Unaffected work I can continue:
Suggested next step:
```

Change requests use:

```
CHANGE REQUEST
From lane:
Target file and owner lane:
Requested change:
Why:
```

Known standing blocker: the supplied database returns "Connection reset", so concrete schema mapping is blocked.

## Mandatory maintenance rule (binding on every coding agent)

The rule is literal: after every code edit, you update three root files: ChangeLog.md, Decisions.md and Flow.md under the `.doclock` protocol. You do not make your next code edit until your own three updates are complete. Documentation-only bookkeeping (the ChangeLog, Decisions and Flow updates themselves, and saving the planning documents at scaffold time) does not trigger another documentation cycle.

Definitions:
- Edits to docs/api.md, docs/roles.md, docs/ownership.md and PROJECT_SPEC.md count as code edits for this rule.
- Your owner string is `<lane>-<short unique id>`, for example `laneB-7f3a`.

What to write:
- ChangeLog.md: append a dated entry describing the change, the files touched, and the tests run with results.
- Decisions.md: record the rationale for any technical decision you actually made. If none, write that no decision changed. Never invent a decision.
- Flow.md: if interactions between components changed, update the flow description and the Mermaid diagram. If unchanged, write that the flow is unchanged. Never invent a flow.

These three files are shared by parallel lanes, so use the lock protocol:

1. Finish your code edit.
2. Acquire a repo-root `.doclock` by atomic exclusive create, with your owner string and a UTC timestamp inside.
   - POSIX shell: `( set -o noclobber; printf 'owner=%s\nacquired=%s\n' "$OWNER" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > .doclock )`
   - Python: `os.open(".doclock", os.O_CREAT | os.O_EXCL | os.O_WRONLY)`, then write the content.
3. If acquisition fails because the file exists, wait and retry (for example every 15 seconds). Read the lock file to see the owner, never write to it. Never overwrite it. Never delete it, including by age: age alone proves nothing. If it appears abandoned or you have waited about 10 minutes, stop and ask the maintainer to resolve it. Do not edit code while waiting.
4. While holding the lock, re-read all three files in full. Append your dated lane entries. Preserve every other agent's entries. Edit the Flow diagram in place only when interactions changed, preserving everything else. Save.
5. Check that your entries are present in all three files.
6. Release by deleting `.doclock` only if its owner line is yours. Only the owner releases, and only after all three updates are complete.
7. If something fails midway, keep the lock, retry, and if you cannot finish, stop and ask the maintainer. Never release with partial updates.

Entry formats:
- ChangeLog.md: `## YYYY-MM-DD | <lane> | <owner string>` then bullets for change, files, tests.
- Decisions.md: `### YYYY-MM-DD | <lane>` then `Decision:`, `Rationale:`, `Alternatives considered:` or `No decision changed.`
- Flow.md: a line in the Flow update log: `YYYY-MM-DD | <lane> | changed: <what>` or `YYYY-MM-DD | <lane> | flow unchanged`.

The initial contents of the three files describe the planned starting state. The scaffold lane saves them verbatim, then appends its own entries through this protocol after creating the skeleton.

## Definition of done for any task

- Code edit complete and within your files.
- Tests run and honestly reported.
- No secrets, no private data, no invented schema names.
- Three maintenance files updated under the lock, lock released.
- Final message: what changed, tests and results, blockers, change requests.