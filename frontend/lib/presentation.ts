import type { CellValue, ChatStatus, EvidenceEntry } from "./types";

export const statusLabels: Record<ChatStatus, string> = {
  answered: "Answered",
  refused: "Refused",
  no_data: "No data",
  needs_clarification: "Needs clarification",
  error: "Error",
};

export const evidenceKindLabels: Record<EvidenceEntry["kind"], string> = {
  tool: "Tool call",
  sql_view: "SQL view",
};

export function roleInitials(label: string): string {
  const words = label.trim().split(/\s+/).filter(Boolean);
  if (words.length === 0) {
    return "?";
  }
  if (words.length === 1) {
    return words[0].slice(0, 2).toUpperCase();
  }
  return `${words[0][0]}${words[words.length - 1][0]}`.toUpperCase();
}

/** Renders a cell exactly as the row carries it. Missing values stay empty. */
export function formatCell(value: CellValue | undefined): string {
  if (value === null || value === undefined) {
    return "";
  }
  return String(value);
}
