import { evidenceKindLabels, formatCell } from "@/lib/presentation";
import type { ChatResponse, EvidenceEntry, Row } from "@/lib/types";
import { InfoIcon } from "./icons";

function previewColumns(entry: EvidenceEntry): string[] {
  if (entry.columns.length > 0) {
    return entry.columns;
  }
  const first = entry.rows_preview[0];
  return first ? Object.keys(first) : [];
}

function previewRows(entry: EvidenceEntry): Row[] {
  return entry.rows_preview;
}

function EvidenceItem({ entry }: { entry: EvidenceEntry }) {
  const columns = previewColumns(entry);
  const rows = previewRows(entry);

  return (
    <li className="evidence-item">
      <div className="evidence-item-top">
        <span className="evidence-kind">{evidenceKindLabels[entry.kind]}</span>
        <span className="evidence-label">{entry.label}</span>
      </div>
      <pre className="evidence-detail">{entry.detail}</pre>
      <div className="evidence-columns">
        {entry.columns.map((column) => (
          <span className="evidence-column" key={column}>
            {column}
          </span>
        ))}
      </div>
      <p className="evidence-meta">
        {`${entry.row_count} ${entry.row_count === 1 ? "row" : "rows"}`}
        {rows.length > 0 && rows.length !== entry.row_count
          ? `, preview of ${rows.length}`
          : ""}
      </p>
      {rows.length > 0 ? (
        <div className="evidence-preview">
          <table>
            <thead>
              <tr>
                {columns.map((column) => (
                  <th key={column} scope="col">
                    {column}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row, rowIndex) => (
                <tr key={rowIndex}>
                  {columns.map((column) => (
                    <td key={column}>{formatCell(row[column])}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
      <time className="evidence-time" dateTime={entry.executed_at}>
        {entry.executed_at}
      </time>
    </li>
  );
}

/**
 * Evidence panel. Shows only the evidence entries and fields the response
 * carries. It never builds evidence from the answer text.
 */
export function EvidencePanel({ response }: { response: ChatResponse | null }) {
  if (!response) {
    return (
      <div className="panel-placeholder">
        <p className="eyebrow">Evidence</p>
        <h2>No response selected</h2>
        <p>Evidence for the selected response appears here.</p>
      </div>
    );
  }

  return (
    <section className="evidence" aria-labelledby="evidence-heading">
      <div className="evidence-heading">
        <div>
          <p className="eyebrow">Evidence</p>
          <h2 id="evidence-heading">Data behind this response</h2>
        </div>
        <span className="evidence-count">{response.evidence.length}</span>
      </div>
      {response.evidence.length > 0 ? (
        <ul className="evidence-list">
          {response.evidence.map((entry) => (
            <EvidenceItem entry={entry} key={entry.id} />
          ))}
        </ul>
      ) : (
        <div className="evidence-empty">
          <InfoIcon size={20} />
          <p>No evidence was returned for this response.</p>
        </div>
      )}
    </section>
  );
}
