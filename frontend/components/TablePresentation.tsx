import { formatCell } from "@/lib/presentation";
import type { TablePresentation as TablePresentationData } from "@/lib/types";

/**
 * Table presentation. Columns and rows come from the response only. The
 * server builds the payload, so this component never computes values.
 */
export function TablePresentation({
  presentation,
}: {
  presentation: TablePresentationData;
}) {
  return (
    <div className="table-block">
      <div className="table-wrap">
        <table>
          <caption className="sr-only">
            {`Table of ${presentation.total_rows} rows`}
          </caption>
          <thead>
            <tr>
              {presentation.columns.map((column) => (
                <th key={column.key} scope="col">
                  {column.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {presentation.rows.map((row, rowIndex) => (
              <tr key={rowIndex}>
                {presentation.columns.map((column) => (
                  <td key={column.key} data-label={column.label}>
                    {formatCell(row[column.key])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="table-meta">
        {`${presentation.total_rows} ${
          presentation.total_rows === 1 ? "row" : "rows"
        } total`}
        {presentation.truncated ? " (truncated)" : ""}
      </p>
    </div>
  );
}
