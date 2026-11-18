import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TablePresentation } from "@/components/TablePresentation";
import type { TablePresentation as TablePresentationData } from "@/lib/types";
import { scenario } from "./scenario";

function tableFixture(): TablePresentationData {
  const presentation = scenario("answered__table").response.presentation;
  if (presentation.type !== "table") {
    throw new Error("answered__table fixture is not a table presentation");
  }
  return presentation;
}

describe("TablePresentation", () => {
  it("renders the contract columns as headers in contract order", () => {
    const presentation = tableFixture();

    render(<TablePresentation presentation={presentation} />);

    const headers = screen.getAllByRole("columnheader");
    expect(headers.map((header) => header.textContent)).toEqual(
      presentation.columns.map((column) => column.label),
    );
  });

  it("renders every executed row value without computing new values", () => {
    const presentation = tableFixture();

    render(<TablePresentation presentation={presentation} />);

    const rows = within(screen.getByRole("table")).getAllByRole("row").slice(1);
    expect(rows).toHaveLength(presentation.rows.length);

    rows.forEach((row, rowIndex) => {
      const cells = within(row).getAllByRole("cell");
      presentation.columns.forEach((column, columnIndex) => {
        expect(cells[columnIndex]).toHaveTextContent(
          String(presentation.rows[rowIndex][column.key]),
        );
      });
    });
  });

  it("shows the contract row total and truncation flag", () => {
    const presentation = tableFixture();

    render(<TablePresentation presentation={presentation} />);

    expect(screen.getByText("1 row total")).toBeInTheDocument();
    expect(screen.queryByText(/truncated/)).not.toBeInTheDocument();
  });

  it("reports truncation from the presentation payload", () => {
    const presentation = { ...tableFixture(), truncated: true, total_rows: 42 };

    render(<TablePresentation presentation={presentation} />);

    expect(screen.getByText("42 rows total (truncated)")).toBeInTheDocument();
  });
});
