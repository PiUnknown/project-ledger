"use client";

import type { FormEvent, KeyboardEvent } from "react";
import { SendIcon } from "./icons";

export function Composer({
  value,
  onChange,
  onSubmit,
  busy,
}: {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  busy: boolean;
}) {
  const canSend = value.trim().length > 0 && !busy;

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (canSend) {
      onSubmit();
    }
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      if (canSend) {
        onSubmit();
      }
    }
  }

  return (
    <div className="composer-wrap">
      <form className="composer" onSubmit={handleSubmit}>
        <textarea
          aria-label="Ask a question"
          maxLength={2000}
          onChange={(event) => onChange(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about items, stock or units in plain English"
          rows={1}
          value={value}
        />
        <button aria-label="Send question" disabled={!canSend} type="submit">
          <SendIcon size={18} />
        </button>
      </form>
      <p>
        Demo responses may be inaccurate. No real company data is used. The
        demo role toggle is not authentication.
      </p>
    </div>
  );
}
