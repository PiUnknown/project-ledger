"use client";

import type { ChatResponse } from "@/lib/types";
import { ChartPresentation } from "./ChartPresentation";
import { TablePresentation } from "./TablePresentation";
import { TextPresentation } from "./TextPresentation";
import { StatusBadge } from "./StatusBadge";

export function AnswerCard({
  question,
  response,
  selected,
  onSelect,
}: {
  question: string;
  response: ChatResponse;
  selected: boolean;
  onSelect: () => void;
}) {
  return (
    <article
      className={`answer-card answer-${response.status}${selected ? " is-selected" : ""}`}
    >
      <div className="answer-topline">
        <div className="answer-badges">
          <StatusBadge status={response.status} />
          {response.reason_code ? (
            <span className="reason-code">{response.reason_code}</span>
          ) : null}
        </div>
        <button
          aria-pressed={selected}
          className="evidence-toggle"
          onClick={onSelect}
          type="button"
        >
          {selected ? "Evidence shown" : "View evidence"}
          <span className="sr-only">{` for ${question}`}</span>
        </button>
      </div>

      {response.presentation.type === "text" ? (
        <TextPresentation text={response.answer_text} />
      ) : (
        <>
          <p className="answer-body">{response.answer_text}</p>
          {response.presentation.type === "table" ? (
            <TablePresentation presentation={response.presentation} />
          ) : (
            <ChartPresentation presentation={response.presentation} />
          )}
        </>
      )}

      {response.notes.length > 0 ? (
        <ul className="answer-notes">
          {response.notes.map((note, index) => (
            <li key={index}>{note}</li>
          ))}
        </ul>
      ) : null}
    </article>
  );
}
