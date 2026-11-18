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