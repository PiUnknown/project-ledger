import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AnswerCard } from "@/components/AnswerCard";
import {
  contractFixtureResponses,
  resolveFixtureResponse,
  type ContractFixtureKey,
} from "@/lib/fixtures";
import { statusLabels } from "@/lib/presentation";
import type { ChatStatus, ReasonCode } from "@/lib/types";
import { scenario } from "./scenario";

const fixtureKeys = Object.keys(
  contractFixtureResponses,
) as ContractFixtureKey[];

describe("AnswerCard status handling", () => {
  it.each(fixtureKeys)(
    "renders the %s contract fixture exactly as Lane A provides it",
    (scenarioId) => {
      const { response } = scenario(scenarioId);

      render(
        <AnswerCard
          onSelect={() => {}}
          question={`Preview contract fixture ${scenarioId}`}
          response={response}
          selected={false}
        />,
      );

      expect(screen.getByText(statusLabels[response.status])).toBeInTheDocument();
      expect(screen.getByText(response.answer_text)).toBeInTheDocument();

      if (response.reason_code) {
        expect(screen.getByText(response.reason_code)).toBeInTheDocument();
      }

      expect(
        screen.getByRole("button", { name: /View evidence/ }),
      ).toBeInTheDocument();
    },
  );

  it("covers every status and presentation pair in the frozen contract", () => {
    const statuses = new Set(
      fixtureKeys.map((key) => key.split("__")[0] as ChatStatus),
    );
    const presentations = new Set(fixtureKeys.map((key) => key.split("__")[1]));

    expect(fixtureKeys).toHaveLength(15);
    expect(statuses).toEqual(
      new Set(["answered", "refused", "no_data", "needs_clarification", "error"]),
    );
    expect(presentations).toEqual(new Set(["text", "table", "chart"]));
  });

  it("marks the selected response for the evidence panel", () => {
    const { response } = scenario("answered__text");

    render(
      <AnswerCard
        onSelect={() => {}}
        question="Preview contract fixture answered__text"
        response={response}
        selected
      />,
    );

    expect(
      screen.getByRole("button", { name: /Evidence shown/ }),
    ).toHaveAttribute("aria-pressed", "true");
  });
});

describe("fixture client mirrors the documented stub behaviour", () => {
  it("returns the documented role_not_configured refusal for purchase_manager", () => {
    const response = resolveFixtureResponse({
      role: "purchase_manager",
      thread_id: "thread_fixture_1",
      message: "Show purchases",
    });

    expect(response.status).toBe("refused");
    expect(response.reason_code).toBe("role_not_configured");
    expect(response.answer_text).toBe("This role is not configured.");
    expect(response.evidence).toEqual([]);
    expect(response.thread_id).toBe("purchase_manager:thread_fixture_1");
  });

  it("answers the fixed demo command with the fabricated sample item table", () => {
    const response = resolveFixtureResponse({
      role: "inventory_manager",
      thread_id: "thread_fixture_2",
      message: "  Show   Sample Items ",
    });

    expect(response.status).toBe("answered");
    expect(response.reason_code).toBeNull();
    expect(response.presentation.type).toBe("table");
    if (response.presentation.type === "table") {
      expect(response.presentation.columns.map((column) => column.key)).toEqual([
        "sample_item",
        "sample_stock",
      ]);
      expect(response.presentation.rows).toEqual([
        { sample_item: "Fabricated item A", sample_stock: 12 },
        { sample_item: "Fabricated item B", sample_stock: 4 },
      ]);
      expect(response.presentation.truncated).toBe(false);
    }
    expect(response.evidence[0].id).toBe("mock-list-sample-items");
  });

  it("clarifies anything else without inventing an answer", () => {
    const response = resolveFixtureResponse({
      role: "owner",
      thread_id: "thread_fixture_3",
      message: "What are our best items?",
    });

    expect(response.status).toBe("needs_clarification");
    expect(response.reason_code).toBe("ambiguous_entity");
    expect(response.evidence).toEqual([]);
    expect(response.presentation).toEqual({ type: "text" });
  });

  it("covers every reason code the contract can return", () => {
    const fromFixtures = fixtureKeys
      .map((key) => contractFixtureResponses[key].reason_code)
      .filter((code): code is ReasonCode => code !== null);
    const fromStub = resolveFixtureResponse({
      role: "purchase_manager",
      thread_id: "thread_fixture_4",
      message: "Any message",
    }).reason_code;

    const all = [...fromFixtures, fromStub as ReasonCode];
    expect(new Set(all)).toEqual(
      new Set<ReasonCode>([
        "outside_role_access",
        "role_not_configured",
        "unsupported_request",
        "data_not_available",
        "ambiguous_entity",
      ]),
    );
  });
});
