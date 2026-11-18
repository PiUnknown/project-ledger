import { act, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { ChatApp } from "@/components/ChatApp";
import { ApiRequestError, FixtureChatClient, type ChatClient } from "@/lib/api";
import { contractHealth, contractRoles } from "@/lib/fixtures";
import type { ChatResponse } from "@/lib/types";
import { scenario } from "./scenario";

describe("loading and transport states", () => {
  it("shows a loading state and renders nothing until the response arrives", async () => {
    const user = userEvent.setup();
    let resolveSend: ((value: ChatResponse) => void) | undefined;

    const pendingClient: ChatClient = {
      listRoles: async () => contractRoles,
      getHealth: async () => contractHealth,
      sendChat: () =>
        new Promise<ChatResponse>((resolve) => {
          resolveSend = resolve;
        }),
    };

    render(<ChatApp client={pendingClient} />);

    const answer = scenario("answered__text").response;
    await user.type(screen.getByLabelText("Ask a question"), "Show stock");
    await user.click(screen.getByRole("button", { name: "Send question" }));

    expect(await screen.findByText("Waiting for the backend")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Send question" })).toBeDisabled();
    expect(screen.queryByText(answer.answer_text)).not.toBeInTheDocument();

    await act(async () => {
      resolveSend?.(answer);
    });

    expect(await screen.findByText(answer.answer_text)).toBeInTheDocument();
    expect(screen.queryByText("Waiting for the backend")).not.toBeInTheDocument();
  });

  it("shows the contract error envelope instead of inventing a response", async () => {
    const user = userEvent.setup();
    const failingClient: ChatClient = {
      listRoles: async () => contractRoles,
      getHealth: async () => contractHealth,
      sendChat: async () => {
        throw new ApiRequestError({
          message: "Rate limit reached. Try again shortly.",
          code: "rate_limited",
          requestId: "fixture-request-error",
          httpStatus: 429,
        });
      },
    };

    render(<ChatApp client={failingClient} />);

    await user.type(screen.getByLabelText("Ask a question"), "Show stock");
    await user.click(screen.getByRole("button", { name: "Send question" }));

    expect(
      await screen.findByText("Rate limit reached. Try again shortly."),
    ).toBeInTheDocument();
    expect(screen.getByText("rate_limited")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Try again/ })).toBeInTheDocument();
  });

  it("returns the effective role-scoped thread id like the backend does", async () => {
    const client = new FixtureChatClient(0);
    const response = await client.sendChat({
      role: "inventory_manager",
      thread_id: "thread-test-1",
      message: "Show stock",
    });

    expect(response.thread_id).toBe("inventory_manager:thread-test-1");
    expect(response.role).toBe("inventory_manager");
    expect(response.contract_version).toBe("0.1");
    expect(response.status).toBe("needs_clarification");
  });
});
