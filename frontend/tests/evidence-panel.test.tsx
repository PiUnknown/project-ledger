import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EvidencePanel } from "@/components/EvidencePanel";
import type { EvidenceEntry } from "@/lib/types";
import { scenario } from "./scenario";

describe("EvidencePanel", () => {
  it("prompts for a selection when no response is selected", () => {
    render(<EvidencePanel response={null} />);

    expect(screen.getByText("No response selected")).toBeInTheDocument();
  });

  it("renders a tool evidence entry from the response fields", () => {
    const { response } = scenario("answered__text");
    const entry = response.evidence[0];

    render(<EvidencePanel response={response} />);

    expect(screen.getByText("Tool call")).toBeInTheDocument();
    expect(screen.getByText(entry.label)).toBeInTheDocument();
    expect(screen.getByText(entry.detail)).toBeInTheDocument();
    expect(screen.getByText("1 row")).toBeInTheDocument();
    expect(screen.getByText(entry.executed_at)).toBeInTheDocument();

    const preview = screen.getByRole("table");
    expect(within(preview).getAllByRole("row")).toHaveLength(
      entry.rows_preview.length + 1,
    );
  });

  it("renders a SQL view entry with its columns", () => {
    // The frozen fixtures only carry kind "tool". docs/api.md also allows
    // "sql_view", so the kind mapping is checked with the same entry fields.
    const base = scenario("answered__text").response.evidence[0];
    const entry: EvidenceEntry = { ...base, kind: "sql_view" };
    const response = {
      ...scenario("answered__text").response,
      evidence: [entry],
    };

    const { container } = render(<EvidencePanel response={response} />);

    expect(screen.getByText("SQL view")).toBeInTheDocument();
    expect(screen.getByText("1")).toBeInTheDocument();

    const chips = Array.from(container.querySelectorAll(".evidence-column")).map(
      (chip) => chip.textContent,
    );
    expect(chips).toEqual(entry.columns);

    expect(screen.getByText(entry.detail)).toBeInTheDocument();
  });

  it("reports an empty evidence list without inventing entries", () => {
    const { response } = scenario("refused__text");

    render(<EvidencePanel response={response} />);

    expect(
      screen.getByText("No evidence was returned for this response."),
    ).toBeInTheDocument();
    expect(screen.getByText("0")).toBeInTheDocument();
    expect(screen.queryByRole("table")).not.toBeInTheDocument();
  });
});
