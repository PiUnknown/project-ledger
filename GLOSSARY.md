# Glossary

Authoritative for terms and role names. Database terms are generic business meanings. Whether and where they exist in the database is pending schema inspection. No table or column names appear here until docs/schema.local.md exists.

## Role names (use exactly these)

- `owner`: UI label "Business Owner". Sees everything in the database. Read-only by default.
- `inventory_manager`: UI label "Inventory Manager". Must never see prices, including indirectly.
- `purchase_manager`: UI label "Purchase Manager". Limits are defined by the maintainer and are pending. Until then the role is not configured.

## Technical terms

- Demo toggle: the UI control that selects a role. It is not authentication.
- Role context: the validated role attached to a request on the server.
- Effective thread id: server-built conversation key combining role and the client thread id, so roles never share history.
- RoleExecutor: the interface through which the agent obtains data for a role. All data access passes through it.
- Mock executor: a fixture-backed RoleExecutor for development before the schema is available.
- Policy: the machine-readable statement of what each role may access. Mirrors docs/roles.md.
- Deny-by-default: anything not explicitly allowed for a role is refused.
- Monetary field: any column or derived value that is a price, cost, sales amount, margin, valuation, or a proxy that encodes one. Which database columns qualify is pending schema inspection.
- Proxy field: a column that reveals a monetary value without being one, such as a tier or a free-text note containing a price.
- Indirect disclosure: revealing monetary information without stating it, for example by ranking, filtering, thresholding, aggregating or deriving.
- Ranking leak: an ordering that reveals relative value.
- Filter oracle: repeated threshold filters that let someone narrow a hidden value.
- Derived value: a value computed from fields, such as quantity times price.
- Guard: a deterministic scan of the final response for forbidden content. Defense in depth only.
- Leak scanner: the function implementing the guard, and its use in evals.
- Evidence: the rows and query information behind an answer, built only from role-visible columns.
- Evidence panel: the UI area showing evidence.
- Presentation: how an answer is shown: `text`, `table` or `chart`.
- Status: outcome of a chat turn: `answered`, `refused`, `no_data`, `needs_clarification`, `error`.
- Refusal: a response with status `refused` for out-of-role requests.
- No data: a response with status `no_data` when the database cannot answer.
- Supplied database: the case provider's database. Never modified. Never touched by coding agents.
- Private copy: the maintainer's own full copy used for development.
- Fabricated dataset: invented data with the same structure, used for anything public.
- Data profile: `private` or `fabricated`, selected by `DATA_PROFILE`.
- Gate G1: the point where docs/schema.local.md exists and the column classification is approved.
- Lane: a parallel unit of agent work with defined file ownership.
- Doclock: the root `.doclock` file guarding ChangeLog.md, Decisions.md and Flow.md.
- Maintenance rule: the literal requirement that after every code edit, the agent updates ChangeLog.md, Decisions.md and Flow.md under the `.doclock` protocol before making the next code edit. Documentation-only bookkeeping does not trigger another cycle.
- Decision: a choice the maintainer has made or an implementation choice an agent made within its lane.
- Proposal: an unresolved choice. Not a decision until the maintainer approves it in Decisions.md.
- Contract: the wire format defined in docs/api.md.

## Business terms (database mapping pending schema inspection)

- Item: a product or material the factory tracks. Pending.
- Stock level: quantity of an item on hand. Pending.
- Reorder level: the stock threshold that triggers replenishment. Whether the database stores it is pending.
- Price: the selling price of an item. Whether it is stored per item, per sale or both is pending.
- Cost price: what the factory pays for an item. Pending.
- Sales: recorded sales transactions. Pending.
- Units sold: quantity sold, which may or may not be stored separately from amounts. Pending.
- Revenue: sales amount. Pending.
- Margin: price minus cost. Derived, so monetary. Pending.
- Stock valuation: stock quantity multiplied by a price or cost. Derived, so monetary. Pending.
- Supplier: who provides an item. Whether the database stores it is pending.
- Category: grouping of items. Whether the database stores it is pending.