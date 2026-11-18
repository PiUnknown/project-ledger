# Roles

Authoritative for role permissions, monetary rules and refusal behavior. Concrete column mapping is pending schema inspection. Rules below hold regardless of the schema. `db/policy/` carries a machine-readable mirror owned by Lane D, which must match this file. Change this file first.

## Defined terms

Monetary field: any column or derived value that is a price, cost, sales amount, margin, valuation, or a proxy that encodes one. Which database columns qualify is decided in `docs/schema.local.md` and approved by the maintainer at gate G1.

## Deny-by-default

For restricted roles, a column is usable only if it is explicitly classified as allowed for that role in the approved classification. Unclassified columns are denied. This applies to selection, filtering, ordering, grouping, joining, aggregating and deriving.

## owner

Sees everything in the database. Read-only by default. Writes only under Lane G and only locally.

## inventory_manager

Allowed: item identity and descriptive attributes, stock levels, reorder information, and units sold if the schema stores units separately from amounts. Existence of each is pending schema inspection. If units can only be derived from amounts, units sold is not available to this role and the agent says so.

Denied, including indirectly:
- Prices, cost, sales amounts, margin, stock valuation, any monetary field.
- Rankings or orderings that depend on a monetary field ("most valuable", "cheapest", "top by revenue").
- Filters, thresholds or counts conditioned on a monetary field ("items priced over X"). Repeated filters would let someone narrow the value.
- Aggregates and derived values involving money: total inventory value, capital tied up, restock cost, ABC analysis by value, averages per category.
- Proxy fields: tiers, grades, bands, and free-text fields containing prices.
- Qualitative price language in answers ("premium", "expensive", "cheaper than").
- Any monetary content in answer text, presentation payloads, evidence, notes, errors, logs or traces. Hidden columns must not appear in payloads even if the frontend would not render them.

Default result ordering for this role must not depend on a monetary field.

## purchase_manager

Not configured. The maintainer defines the limits. Until then, every chat request for this role returns status `refused` with reason code `role_not_configured`, and `/api/roles` reports `configured: false`.

Proposal P-003 (not decided): sees cost price, supplier and stock data and sales volume, but not selling price, margin or revenue. Pending the maintainer and the schema.

## Refusal behavior

- Say the information is outside this role's access. Offer what the role can answer.
- Do not name hidden columns, quote hidden values, or confirm specific relationships between hidden values.
- Do not reveal the reason beyond the access boundary.
- Refusals use status `refused` with reason code `outside_role_access`.

## No-data behavior (all roles)

If the database cannot answer (market prices, causes, anything not stored), return status `no_data` with reason code `data_not_available`, say what the data does contain that is related, and invent nothing.

## Evidence rules

Evidence for a role may contain only columns that role may see. Query text or tool parameters shown as evidence pass the same rule.

## Isolation

Each role has its own conversation. Switching roles never carries history across.