import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ChartPresentation } from "@/components/ChartPresentation";
import type { ChartPresentation as ChartPresentationData } from "@/lib/types";
import { scenario } from "./scenario";

function chartFixture(): ChartPresentationData {
  const presentation = scenario("answered__chart").response.presentation;
  if (presentation.type !== "chart") {
    throw new Error("answered__chart fixture is not a chart presentation");
  }
  return presentation;
}

function expectRowsMatch(presentation: ChartPresentationData) {
  const table = screen.getByRole("table");
  const rows = within(table).getAllByRole("row").slice(1);

  expect(rows).toHaveLength(presentation.rows.length);

  rows.forEach((row, rowIndex) => {
    const cells = within(row).getAllByRole("cell");
    expect(cells[0]).toHaveTextContent(
      String(presentation.rows[rowIndex][presentation.x.key]),
    );
    presentation.series.forEach((series, seriesIndex) => {
      expect(cells[seriesIndex + 1]).toHaveTextContent(
        String(presentation.rows[rowIndex][series.key]),
      );
    });
  });
}

describe("ChartPresentation", () => {
  it("renders the contract bar chart from the payload", () => {
    const presentation = chartFixture();

    render(<ChartPresentation presentation={presentation} />);

    expect(screen.getByRole("figure")).toHaveAttribute("data-chart-kind", "bar");
    expect(
      screen.getByText(presentation.title, { selector: "figcaption" }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("columnheader", { name: presentation.x.label }),
    ).toBeInTheDocument();
    presentation.series.forEach((series) => {
      expect(
        screen.getByRole("columnheader", { name: series.label }),
      ).toBeInTheDocument();
    });
    expectRowsMatch(presentation);
  });

  it("renders the line variant that docs/api.md also allows", () => {
    // Lane A's frozen fixtures only carry kind "bar". docs/api.md allows
    // "bar | line", so the renderer is checked against the other documented
    // variant using the same contract rows. No row value is changed.
    const presentation: ChartPresentationData = {
      ...chartFixture(),
      kind: "line",
    };

    render(<ChartPresentation presentation={presentation} />);

    expect(screen.getByRole("figure")).toHaveAttribute("data-chart-kind", "line");
    expectRowsMatch(presentation);
  });

  it("reports truncation only when the payload says so", () => {
    const truncated: ChartPresentationData = { ...chartFixture(), truncated: true };
    const { unmount } = render(<ChartPresentation presentation={truncated} />);

    expect(
      screen.getByText("Rows truncated to the configured row limit."),
    ).toBeInTheDocument();

    unmount();

    render(<ChartPresentation presentation={chartFixture()} />);

    expect(screen.queryByText(/truncated/i)).not.toBeInTheDocument();
  });
});
