# API contract

Authoritative for endpoints, request and response shapes, and error codes. Contract version: 0.1. Lane A owns changes. `backend/app/schemas.py` and `frontend/lib/types.ts` must mirror this file. Change this file first, then the code, following docs/ownership.md.

All bodies are JSON. Single response per request in v0.1, no streaming.

## GET /api/health

Response 200: `{ "status": "ok", "contract_version": "0.1", "data_profile": "private" | "fabricated" }`

## GET /api/roles

Response 200: a list of `{ "id": string, "label": string, "description": string, "configured": boolean }`. Ids are `owner`, `inventory_manager`, `purchase_manager`. Descriptions must not reveal any data. `purchase_manager` has `configured: false` until its limits are defined in docs/roles.md.

## POST /api/chat

Request:

```json
{
  "role": "owner",
  "thread_id": "string, 8 to 64 characters, letters, digits, underscore, hyphen",
  "message": "string, 1 to 2000 characters"
}
```

The server forms the effective thread id from role and `thread_id`, so roles never share history. Clients should generate a new `thread_id` when the role changes. The server guarantees isolation regardless.

The `thread_id` constraint above applies to the client-supplied request value only. The response `thread_id` is the server-built effective id: `{role}:{client_thread_id}`. For example, request value `thread_123` becomes response value `owner:thread_123` or `inventory_manager:thread_123`. The response value contains a colon and is not subject to the request validator's letters, digits, underscore and hyphen pattern.

Response 200:

```json
{
  "contract_version": "0.1",
  "request_id": "string",
  "role": "owner",
  "thread_id": "string",
  "status": "answered",
  "reason_code": null,
  "answer_text": "string",
  "presentation": { "type": "text" },
  "evidence": [],
  "notes": []
}
```

Fields:
- `status`: `answered`, `refused`, `no_data`, `needs_clarification`, `error`.
- `reason_code`: null when `answered`. Otherwise one of `outside_role_access`, `role_not_configured`, `unsupported_request`, `data_not_available`, `ambiguous_entity`.
- `answer_text`: plain text for every status. Never names hidden fields or values.
- `presentation`: one of the variants below.
- `evidence`: list of evidence entries. Required non-empty when `status` is `answered`.
- `notes`: optional caveats, for example truncation or date anchoring.

Presentation variants:

```json
{ "type": "text" }
```

```json
{
  "type": "table",
  "columns": [{ "key": "string", "label": "string", "type": "string | number | integer | date | boolean" }],
  "rows": [{ "key": "value" }],
  "total_rows": 0,
  "truncated": false
}
```

```json
{
  "type": "chart",
  "kind": "bar | line",
  "title": "string",
  "x": { "key": "string", "label": "string", "type": "string | number | integer | date" },
  "series": [{ "key": "string", "label": "string" }],
  "rows": [{ "key": "value" }],
  "truncated": false
}
```

Table and chart `rows` are the executed rows. The server builds them. The model never supplies the data array.

Evidence entry:

```json
{
  "id": "string",
  "kind": "tool | sql_view",
  "label": "string",
  "detail": "role-visible tool parameters or query text",
  "columns": ["string"],
  "row_count": 0,
  "rows_preview": [{ "key": "value" }],
  "executed_at": "ISO 8601 timestamp"
}
```

Evidence is built only from columns the role may see (docs/roles.md). Preview is capped by `QUERY_ROW_LIMIT`.

Domain outcomes (answered, refused, no_data, needs_clarification) always return HTTP 200 with a `status`.

## Contract support and current stub output

The v0.1 response schema supports all three role ids (`owner`, `inventory_manager`, `purchase_manager`), both chart kinds (`bar`, `line`), and both evidence kinds (`tool`, `sql_view`). The current stub emits a narrower set; this does not reduce the contract's supported values.

The current default stub behaves as follows:

- For `owner` and `inventory_manager`, the fixed commands `list sample items`, `show sample items` and `show demo items` return `answered` with a table and `tool` evidence from the fabricated mock.
- Other messages for those roles return `needs_clarification` with a text presentation and no evidence.
- `purchase_manager` returns `refused` with reason `role_not_configured`, a text presentation and no evidence.
- The stub has a `no_data` branch if an executor returns no rows, but the default mock fixture contains two rows. The stub does not emit charts or `sql_view` evidence.
- The HTTP handler returns transport and unexpected failures as the error envelope below. It does not emit a `ChatResponse` with status `error`.

The 15 examples in `backend/tests/api/contract_fixtures.py` are synthetic model-validation fixtures, not snapshots of current endpoint responses. They cover every status and presentation pair. The `answered__table` fixture uses `inventory_manager`; `refused__text` uses `purchase_manager` with `role_not_configured`; and `answered__chart` uses the schema-supported `line` chart kind and `sql_view` evidence. Those latter chart and evidence variants are fixture-only for now. Fixture rows and keys are synthetic and do not describe database schema.

## Errors

Transport and contract problems return an HTTP error with:

```json
{ "error": { "code": "string", "message": "string", "request_id": "string" } }
```

| HTTP | code | Meaning |
|---|---|---|
| 422 | `validation_error` | Malformed request |
| 422 | `invalid_role` | Unknown role |
| 429 | `rate_limited` | Per-IP limit exceeded |
| 429 | `daily_cap_reached` | Global daily request cap reached |
| 502 | `upstream_error` | Model provider failure |
| 504 | `query_timeout` | Query exceeded `QUERY_TIMEOUT_MS` |
| 500 | `internal_error` | Unexpected failure |

Error messages must not reveal hidden field names, values, SQL or stack traces.

## Internal RoleExecutor interface

This section documents the current backend Python interface for implementation and conformance tests. It is an internal implementation detail, not part of the v0.1 HTTP wire contract. It does not define or change an HTTP request or response shape.

The interface is `RoleExecutor.execute` in `backend/app/enforcement/interface.py`:

```python
execute(
    context: RoleContext,
    operation: str,
    parameters: Mapping[str, Any],
    *,
    row_limit: int,
    timeout_ms: int,
) -> ExecutionResult
```

`RoleContext` contains the server-validated `Role` enum (`owner`, `inventory_manager` or `purchase_manager`). It is created from the request's `role` field. Implementations must use this context for access decisions and must not infer a role from `operation`, `parameters` or message text.

| Input | Type | Meaning |
|---|---|---|
| `context` | `RoleContext` | Validated role for this operation |
| `operation` | `str` | Named operation selected by the agent; it is not SQL |
| `parameters` | `Mapping[str, Any]` | Typed operation parameters; the current mock accepts an empty mapping only |
| `row_limit` | `int` | Positive maximum number of rows returned in `result.rows` |
| `timeout_ms` | `int` | Positive execution-time budget in milliseconds |

The method returns an `ExecutionResult` dataclass with this shape:

```python
ExecutionResult(
    columns: tuple[TableColumn, ...],
    rows: tuple[dict[str, Any], ...],
    total_rows: int,
    truncated: bool,
    evidence: EvidenceEntry,
)
```

`TableColumn` and `EvidenceEntry` use the shapes defined in the presentation and evidence sections above. For the current mock, `result.rows` contains at most `row_limit` rows, `total_rows` is the count before applying that limit, and `truncated` is true when rows were omitted. The mock sets `evidence.row_count` to the number of returned rows and includes those rows in `evidence.rows_preview`.

`timeout_ms` is passed to the executor. The current fixture-backed mock validates that it is positive but does not measure elapsed time because its local fixture operation does not wait on an external resource. An executor that can exceed the budget raises `QueryTimeout`; the chat route maps that exception to HTTP 504 with error code `query_timeout` and a generic message that does not expose the exception detail.

The executor exceptions are Python exceptions, not structured HTTP error bodies:

| Exception | Meaning and current mock behavior |
|---|---|
| `ExecutionDenied` | Operation is not allowed. The mock raises `ExecutionDenied("unsupported_operation")` unless `operation` is `list_sample_items` and `parameters` is empty. |
| `RoleNotConfigured` | The role has no configured access policy. The mock raises `RoleNotConfigured("role_not_configured")` for `purchase_manager`; the chat route normally returns the documented `refused` domain response before calling the executor. |
| `QueryTimeout` | Executor detected that the operation exceeded `timeout_ms`. The public HTTP error is the documented 504 `query_timeout` response; exception text is not returned. |
| `ValueError` | The mock raises `ValueError("row_limit must be positive")` or `ValueError("timeout_ms must be positive")` for non-positive limits. Unexpected exceptions reaching the chat route are returned as the documented generic 500 `internal_error`. |

## Reserved for the bonus lane, not part of v0.1

`pending_action` on chat responses and POST `/api/actions/confirm`. Do not implement until the maintainer approves Lane G.
