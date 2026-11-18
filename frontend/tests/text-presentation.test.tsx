import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TextPresentation } from "@/components/TextPresentation";
import { scenario } from "./scenario";

describe("TextPresentation", () => {
  it("renders the answer text exactly as the response carries it", () => {
    const { response } = scenario("answered__text");

    render(<TextPresentation text={response.answer_text} />);

    expect(screen.getByText(response.answer_text)).toBeInTheDocument();
    expect(screen.queryByRole("table")).not.toBeInTheDocument();
    expect(screen.queryByRole("figure")).not.toBeInTheDocument();
  });

  it("renders refusal text without adding its own explanation", () => {
    const { response } = scenario("refused__text");

    render(<TextPresentation text={response.answer_text} />);

    expect(screen.getByText(response.answer_text)).toBeInTheDocument();
    expect(screen.queryByText(/price/i)).not.toBeInTheDocument();
  });
});
