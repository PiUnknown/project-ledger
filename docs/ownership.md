# Ownership

Authoritative for who may edit which file and for the contract change procedure. PROJECT_SPEC.md summarizes lanes. This file wins on conflict.

## Lanes and files

| Path | Owner |
|---|---|
| AGENTS.md, PROJECT_SPEC.md, docs/ownership.md, docs/roles.md | Maintainer. Agents edit only with an explicit maintainer instruction, logged under the lock |
| docs/api.md | Lane A |
| README.md | Section owners: Setup and layout, Lane 0. Backend section, Lane A. Agent section, Lane B. Frontend section, Lane C. Data section, Lane D. Evals section, Lane E. Deployment and Limitations, Lane F |
| GLOSSARY.md | Lane 0 for role names and technical terms. Lane D for business and database terms. Each lane edits only its own section |
| ChangeLog.md, Decisions.md, Flow.md | Shared by all lanes under the `.doclock` protocol in AGENTS.md |
| docs/schema.local.md | Maintainer, local only, gitignored |
| docs/data-model.md | Lane D, only after the maintainer approves publishing (P-011) |
| `.gitignore`, `backend/.env.example`, `frontend/.env.local.example`, tooling config, CI skeleton | Lane 0 first, then Lane F |
| `backend/requirements*.txt`, `frontend/package.json` | Append-only for any lane adding a dependency its own code needs, recorded in Decisions.md |
| `backend/app/main.py`, `config.py`, `schemas.py`, `api/`, `roles/`, `limits/` | Lane A |
| `backend/app/enforcement/interface.py` and the mock executor | Lane A |
| `backend/app/enforcement/` implementations, policy loader, query validation | Lane D |
| `backend/app/agent/` | Lane B |
| `backend/app/guard/` | Lane E |
| `backend/tests/api/` | Lane A |
| `backend/tests/agent/` | Lane B |
| `backend/tests/enforcement/` | Lane D |
| `backend/tests/security/`, `evals/` | Lane E |
| `frontend/` including `lib/types.ts` | Lane C. `lib/types.ts` must mirror docs/api.md |
| `db/policy/`, `db/views/`, `db/seed/`, `db/migrations/` | Lane D |
| `.github/workflows/`, `scripts/`, deployment config | Lane F |
| Bonus write code and tests | Lane G, only after approval |

## Edit rules

- Edit only files you own. Use the change request template in AGENTS.md for anything else.
- Append-only files are never rewritten wholesale.
- Fixtures and tests use fabricated data only.

## Contract change procedure

1. Lane A edits docs/api.md first and bumps `contract_version` if the shape changes.
2. Lane A updates `schemas.py` and mock fixtures.
3. Lane A records the change in ChangeLog.md marked CONTRACT CHANGE.
4. Lane C updates `lib/types.ts` and renderers. Lane B and Lane E update their consumers.
5. Nobody else edits the contract.

## Interface change procedure

The `RoleExecutor` interface is owned by Lane A. Lanes B and D consume it. Changes follow the same steps as the contract, with Lane B and Lane D updating their code after Lane A.