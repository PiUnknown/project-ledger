/**
 * Wire types for the frontend. These mirror docs/api.md contract version 0.1.
 *
 * docs/api.md is authoritative. docs/ownership.md requires this file to mirror
 * it. Change docs/api.md first, then this file.
 */

export const CONTRACT_VERSION = "0.1";

/** Role ids are fixed by docs/api.md and GLOSSARY.md. */
export type RoleId = "owner" | "inventory_manager" | "purchase_manager";

/** GET /api/roles item. */
export interface RoleSummary {
  id: RoleId;
  label: string;
  description: string;
  configured: boolean;
}

/** POST /api/chat status values. */
export type ChatStatus =
  | "answered"
  | "refused"
  | "no_data"
  | "needs_clarification"
  | "error";

/** Non-null reason codes allowed by docs/api.md. */
export type ReasonCode =
  | "outside_role_access"
  | "role_not_configured"
  | "unsupported_request"
  | "data_not_available"
  | "ambiguous_entity";

/** Column types allowed in a table presentation. */
export type ColumnType = "string" | "number" | "integer" | "date" | "boolean";

/** Chart axis types exclude boolean, per docs/api.md. */
export type AxisType = Exclude<ColumnType, "boolean">;

/** Cell values are whatever the server put in an executed row. */
export type CellValue = string | number | boolean | null;

/** A row keyed by presentation column key. */
export type Row = Record<string, CellValue>;

export interface TextPresentation {
  type: "text";
}

export interface TableColumn {
  key: string;
  label: string;
  type: ColumnType;
}

export interface TablePresentation {
  type: "table";
  columns: TableColumn[];
  rows: Row[];
  total_rows: number;
  truncated: boolean;
}

export interface ChartSeries {
  key: string;
  label: string;
}

export interface ChartPresentation {
  type: "chart";
  kind: "bar" | "line";
  title: string;
  x: { key: string; label: string; type: AxisType };
  series: ChartSeries[];
  rows: Row[];
  truncated: boolean;
}

export type Presentation =
  | TextPresentation
  | TablePresentation
  | ChartPresentation;

export interface EvidenceEntry {
  id: string;
  kind: "tool" | "sql_view";
  label: string;
  detail: string;
  columns: string[];
  row_count: number;
  rows_preview: Row[];
  executed_at: string;
}

export interface ChatRequest {
  role: RoleId;
  thread_id: string;
  message: string;
}

export interface ChatResponse {
  contract_version: string;
  request_id: string;
  role: RoleId;
  thread_id: string;
  status: ChatStatus;
  reason_code: ReasonCode | null;
  answer_text: string;
  presentation: Presentation;
  evidence: EvidenceEntry[];
  notes: string[];
}

/** GET /api/health. */
export interface HealthResponse {
  status: "ok";
  contract_version: string;
  data_profile: "private" | "fabricated";
}

/** Error envelope for transport and contract problems, per docs/api.md. */
export interface ApiErrorBody {
  code: string;
  message: string;
  request_id: string;
}

export interface ApiErrorEnvelope {
  error: ApiErrorBody;
}

export function isApiErrorEnvelope(value: unknown): value is ApiErrorEnvelope {
  if (typeof value !== "object" || value === null) {
    return false;
  }
  const candidate = (value as { error?: unknown }).error;
  if (typeof candidate !== "object" || candidate === null) {
    return false;
  }
  const body = candidate as Record<string, unknown>;
  return (
    typeof body.code === "string" &&
    typeof body.message === "string" &&
    typeof body.request_id === "string"
  );
}
