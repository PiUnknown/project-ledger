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

## Reserved for the bonus lane, not part of v0.1

`pending_action` on chat responses and POST `/api/actions/confirm`. Do not implement until the maintainer approves Lane G.