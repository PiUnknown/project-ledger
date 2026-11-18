/**
 * Contract fixtures for the fixture-backed client.
 *
 * Source: Lane A's frozen contract v0.1. Nothing in this file is invented by
 * Lane C.
 * - The 15 response fixtures are transcribed from
 *   backend/tests/api/contract_fixtures.py, function
 *   contract_response_fixtures(): one key per status and presentation pair.
 * - The role list and the health payload are copied from
 *   backend/app/main.py, routes /api/roles and /api/health.
 * - The refusal, clarification and answered sample-item texts mirror
 *   backend/app/api/agent_stub.py. The sample item columns, rows and evidence
 *   mirror backend/app/enforcement/mock_executor.py, with rows from
 *   backend/app/enforcement/fixtures/mock_items.json.
 *
 * Every value is fabricated by Lane A, as its fixture file states. No company
 * data, no table or column from the supplied database, and no monetary value.
 * The UI adds no role logic: it renders these responses as they arrive.
 *
 * tests/contract-fixture-parity.test.ts compares the 15 responses against
 * tests/contract-fixtures.snapshot.json, which was generated from the Python
 * source. Regenerate that snapshot when Lane A changes the fixtures.
 */

import { CONTRACT_VERSION } from "./types";
import type {
  ChatRequest,
  ChatResponse,
  ChatStatus,
  EvidenceEntry,
  HealthResponse,
  Presentation,
  ReasonCode,
  RoleSummary,
  Row,
  TableColumn,
} from "./types";

type PresentationKind = "text" | "table" | "chart";

export type ContractFixtureKey = `${ChatStatus}__${PresentationKind}`;

/** Status to reason_code map from Lane A's fixture module. */
const statusReasonCodes: Record<ChatStatus, ReasonCode | null> = {
  answered: null,
  refused: "outside_role_access",
  no_data: "data_not_available",
  needs_clarification: "ambiguous_entity",
  error: "unsupported_request",
};

const fixtureRows: Row[] = [{ fixture_value: "Fabricated contract row" }];

const fixtureEvidence: EvidenceEntry = {
  id: "fixture-evidence",
  kind: "tool",
  label: "Fabricated fixture",
  detail: "Synthetic contract fixture.",
  columns: ["fixture_value"],
  row_count: 1,
  rows_preview: [{ fixture_value: "Fabricated contract row" }],
  executed_at: "2026-01-01T00:00:00+00:00",
};

/** Mirrors _presentation(kind) in Lane A's fixture module. */
function fixturePresentation(kind: PresentationKind): Presentation {
  if (kind === "text") {
    return { type: "text" };
  }
  if (kind === "table") {
    return {
      type: "table",
      columns: [{ key: "fixture_value", label: "Fixture value", type: "string" }],
      rows: fixtureRows,
      total_rows: 1,
      truncated: false,
    };
  }
  return {
    type: "chart",
    kind: "bar",
    title: "Fabricated contract chart",
    x: { key: "fixture_x", label: "Fixture x", type: "string" },
    series: [{ key: "fixture_y", label: "Fixture y" }],
    rows: [{ fixture_x: "A", fixture_y: 1 }],
    truncated: false,
  };
}

const statuses: ChatStatus[] = [
  "answered",
  "refused",
  "no_data",
  "needs_clarification",
  "error",
];
const presentationKinds: PresentationKind[] = ["text", "table", "chart"];

function buildContractFixtures(): Record<ContractFixtureKey, ChatResponse> {
  const fixtures = {} as Record<ContractFixtureKey, ChatResponse>;

  for (const status of statuses) {
    for (const kind of presentationKinds) {
      const key = `${status}__${kind}` as ContractFixtureKey;
      fixtures[key] = {
        contract_version: CONTRACT_VERSION,
        request_id: `fixture-${key}`,
        role: "owner",
        thread_id: "owner:fixture_thread",
        status,
        reason_code: statusReasonCodes[status],
        answer_text: "Fabricated contract fixture.",
        presentation: fixturePresentation(kind),
        evidence: status === "answered" ? [fixtureEvidence] : [],
        notes: [],
      };
    }
  }

  return fixtures;
}

/** The 15 frozen contract responses, keyed status__presentation. */
export const contractFixtureResponses = buildContractFixtures();

export interface ContractFixtureScenario {
  id: ContractFixtureKey;
  label: string;
  question: string;
  response: ChatResponse;
}

/** Sidebar list of every contract fixture, so each status can be seen. */
export const contractFixtureScenarios: ContractFixtureScenario[] = (
  Object.keys(contractFixtureResponses) as ContractFixtureKey[]
).map((id) => {
  const [status, kind] = id.split("__") as [ChatStatus, PresentationKind];
  return {
    id,
    label: `${status}, ${kind}`,
    question: `Preview contract fixture ${id}`,
    response: contractFixtureResponses[id],
  };
});

/** Copied from GET /api/roles in backend/app/main.py. */
export const contractRoles: RoleSummary[] = [
  {
    id: "owner",
    label: "Business Owner",
    description: "Demo role with broad read access.",
    configured: true,
  },
  {
    id: "inventory_manager",
    label: "Inventory Manager",
    description: "Demo role for inventory questions.",
    configured: true,
  },
  {
    id: "purchase_manager",
    label: "Purchase Manager",
    description: "Access is not configured.",
    configured: false,
  },
];

/** Copied from GET /api/health in backend/app/main.py with the local profile. */
export const contractHealth: HealthResponse = {
  status: "ok",
  contract_version: CONTRACT_VERSION,
  data_profile: "fabricated",
};

/**
 * Live-chat mirror of backend/app/api/agent_stub.py. The stub refuses
 * purchase_manager, answers three fixed demo commands with one table, and
 * clarifies anything else. It never decides a role from message text.
 */
const demoCommands = new Set([
  "list sample items",
  "show sample items",
  "show demo items",
]);

/** Columns and rows from backend/app/enforcement/fixtures/mock_items.json. */
const sampleItemColumns: TableColumn[] = [
  { key: "sample_item", label: "Sample item", type: "string" },
  { key: "sample_stock", label: "Sample stock", type: "integer" },
];

const sampleItemRows: Row[] = [
  { sample_item: "Fabricated item A", sample_stock: 12 },
  { sample_item: "Fabricated item B", sample_stock: 4 },
];

function envelope(request: ChatRequest, suffix: string) {
  return {
    contract_version: CONTRACT_VERSION,
    request_id: `fixture-${suffix}-${request.thread_id.slice(0, 8)}`,
    role: request.role,
    thread_id: `${request.role}:${request.thread_id}`,
  };
}

/**
 * Fixture replacement for POST /api/chat. It reproduces the documented
 * behaviour of Lane A's stub agent for the selected role, using Lane A's
 * texts, columns and rows. The request role is passed through unchanged.
 */
export function resolveFixtureResponse(request: ChatRequest): ChatResponse {
  if (request.role === "purchase_manager") {
    return {
      ...envelope(request, "refused"),
      status: "refused",
      reason_code: "role_not_configured",
      answer_text: "This role is not configured.",
      presentation: { type: "text" },
      evidence: [],
      notes: [],
    };
  }

  const command = request.message.toLowerCase().trim().split(/\s+/).join(" ");

  if (demoCommands.has(command)) {
    return {
      ...envelope(request, "answered-table"),
      status: "answered",
      reason_code: null,
      answer_text: "These are the fabricated sample items.",
      presentation: {
        type: "table",
        columns: sampleItemColumns,
        rows: sampleItemRows,
        total_rows: sampleItemRows.length,
        truncated: false,
      },
      evidence: [
        {
          id: "mock-list-sample-items",
          kind: "tool",
          label: "Fabricated sample items",
          detail: "Fixture-backed mock operation: list_sample_items",
          columns: ["sample_item", "sample_stock"],
          row_count: sampleItemRows.length,
          rows_preview: sampleItemRows,
          executed_at: new Date().toISOString(),
        },
      ],
      notes: [],
    };
  }

  return {
    ...envelope(request, "needs-clarification"),
    status: "needs_clarification",
    reason_code: "ambiguous_entity",
    answer_text: "Please clarify which item or inventory detail you want to check.",
    presentation: { type: "text" },
    evidence: [],
    notes: [],
  };
}
