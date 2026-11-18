import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { ChatApp } from "@/components/ChatApp";
import { FixtureChatClient } from "@/lib/api";
import { resolveFixtureResponse } from "@/lib/fixtures";
import { isValidThreadId } from "@/lib/thread";
import { scenario } from "./scenario";

function appShell(container: HTMLElement): HTMLElement {
  const shell = container.querySelector<HTMLElement>(".app-shell");
  if (!shell) {
    throw new Error("app shell not rendered");
  }
  return shell;
}

async function waitForThread(container: HTMLElement): Promise<string> {
  await waitFor(() => {
    expect(isValidThreadId(appShell(container).dataset.threadId ?? "")).toBe(true);
  });
  return appShell(container).dataset.threadId ?? "";
}

function roleButton(name: RegExp): HTMLElement {
  return within(screen.getByRole("group", { name: "Demo role" })).getByRole(
    "button",
    { name },
  );
}

describe("role switch", () => {
  it("starts a new thread id and clears the visible conversation", async () => {
    const user = userEvent.setup();
    const { container } = render(<ChatApp client={new FixtureChatClient(0)} />);

    expect(appShell(container)).toHaveAttribute("data-role", "owner");

    const expected = resolveFixtureResponse({
      role: "owner",
      thread_id: "thread_expected_1",
      message: "Show the sample stock",
    });

    await user.type(
      screen.getByLabelText("Ask a question"),
      "Show the sample stock",
    );
    await user.click(screen.getByRole("button", { name: "Send question" }));

    expect(await screen.findByText(expected.answer_text)).toBeInTheDocument();
    expect(screen.getByText("Show the sample stock")).toBeInTheDocument();

    const firstThreadId = await waitForThread(container);

    await user.click(roleButton(/Inventory Manager/i));

    await waitFor(() => {
      expect(appShell(container)).toHaveAttribute(
        "data-role",
        "inventory_manager",
      );
    });

    const secondThreadId = await waitForThread(container);
    expect(secondThreadId).not.toBe(firstThreadId);
    expect(isValidThreadId(secondThreadId)).toBe(true);

    expect(screen.queryByText(expected.answer_text)).not.toBeInTheDocument();
    expect(screen.queryByText("Show the sample stock")).not.toBeInTheDocument();
    expect(
      screen.getByText("New conversation for Inventory Manager"),
    ).toBeInTheDocument();
    expect(roleButton(/Inventory Manager/i)).toHaveAttribute(
      "aria-pressed",
      "true",
    );
  });

  it("surfaces the documented role_not_configured refusal from the fixture client", async () => {
    const user = userEvent.setup();
    const { container } = render(<ChatApp client={new FixtureChatClient(0)} />);

    await user.click(roleButton(/Purchase Manager/i));
    await waitForThread(container);

    await user.type(screen.getByLabelText("Ask a question"), "Show purchases");
    await user.click(screen.getByRole("button", { name: "Send question" }));

    const refusal = resolveFixtureResponse({
      role: "purchase_manager",
      thread_id: "thread_expected_2",
      message: "Show purchases",
    });
    expect(await screen.findByText(refusal.answer_text)).toBeInTheDocument();
    expect(screen.getByText("role_not_configured")).toBeInTheDocument();
    expect(screen.getByText("Refused")).toBeInTheDocument();
  });

  it("previews a contract fixture without changing the selected role", async () => {
    const user = userEvent.setup();
    const { container } = render(<ChatApp client={new FixtureChatClient(0)} />);

    const { response } = scenario("answered__table");
    await user.click(
      screen.getByRole("button", { name: /answered, table/i }),
    );

    expect(await screen.findByText(response.answer_text)).toBeInTheDocument();
    expect(appShell(container)).toHaveAttribute("data-role", "owner");
    expect(appShell(container)).toHaveAttribute("data-fixtures", "contract");
  });

  it("keeps the demo toggle note visible", () => {
    const { container } = render(<ChatApp client={new FixtureChatClient(0)} />);

    expect(container.querySelector(".app-shell")).toBeInTheDocument();

    expect(
      screen.getByText("Demo role. Not authentication."),
    ).toBeInTheDocument();
  });
});
