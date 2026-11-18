"use client";

import { useEffect, useRef, useState } from "react";
import {
  ApiRequestError,
  createChatClient,
  usingFixtureResponses,
  type ChatClient,
} from "@/lib/api";
import { contractFixtureScenarios, contractRoles } from "@/lib/fixtures";
import { statusLabels } from "@/lib/presentation";
import { createThreadId } from "@/lib/thread";
import type {
  ChatResponse,
  HealthResponse,
  RoleId,
  RoleSummary,
} from "@/lib/types";
import { AnswerCard } from "./AnswerCard";
import { Composer } from "./Composer";
import { EvidencePanel } from "./EvidencePanel";
import { RoleToggle } from "./RoleToggle";
import {
  AgentIcon,
  ChatIcon,
  CloseIcon,
  InfoIcon,
  MenuIcon,
  PlusIcon,
  RetryIcon,
} from "./icons";

type Turn =
  | { id: string; question: string; state: "pending" }
  | { id: string; question: string; state: "ready"; response: ChatResponse }
  | {
      id: string;
      question: string;
      state: "failed";
      message: string;
      code: string | null;
    };

function describeFailure(error: unknown): { message: string; code: string | null } {
  if (error instanceof ApiRequestError) {
    return { message: error.message, code: error.code };
  }
  return {
    message:
      "The request could not be completed. Check that the backend is running, then try again.",
    code: null,
  };
}

export function ChatApp({ client: providedClient }: { client?: ChatClient } = {}) {
  const [client] = useState<ChatClient>(() => providedClient ?? createChatClient());
  const fixturesMode = usingFixtureResponses();

  const [roles, setRoles] = useState<RoleSummary[]>(contractRoles);
  const [rolesFailed, setRolesFailed] = useState(false);
  const [roleId, setRoleId] = useState<RoleId>("owner");
  const [threadId, setThreadId] = useState("");
  const [turns, setTurns] = useState<Turn[]>([]);
  const [selectedTurnId, setSelectedTurnId] = useState<string | null>(null);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const requestRef = useRef(0);
  const turnCounter = useRef(0);
  const bottomRef = useRef<HTMLDivElement>(null);

  const activeRole = roles.find((role) => role.id === roleId) ?? {
    id: roleId,
    label: roleId,
    description: "",
    configured: true,
  };

  useEffect(() => {
    let cancelled = false;

    client
      .listRoles()
      .then((list) => {
        if (!cancelled && Array.isArray(list) && list.length > 0) {
          setRoles(list);
          setRolesFailed(false);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setRolesFailed(true);
        }
      });

    client
      .getHealth()
      .then((result) => {
        if (!cancelled) {
          setHealth(result);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setHealth(null);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [client]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [turns.length, busy]);

  function nextTurnId(): string {
    turnCounter.current += 1;
    return `turn-${turnCounter.current}`;
  }

  function startFreshConversation() {
    requestRef.current += 1;
    setThreadId(createThreadId());
    setTurns([]);
    setSelectedTurnId(null);
    setInput("");
    setBusy(false);
    setSidebarOpen(false);
  }

  function switchRole(nextRole: RoleId) {
    if (nextRole === roleId) {
      return;
    }
    requestRef.current += 1;
    setRoleId(nextRole);
    setThreadId(createThreadId());
    setTurns([]);
    setSelectedTurnId(null);
    setInput("");
    setBusy(false);
    setSidebarOpen(false);
  }

  async function send(question: string) {
    const trimmed = question.trim();
    if (!trimmed || busy) {
      return;
    }

    // The first message creates the thread id. Role switches and the new
    // conversation button create a fresh one immediately.
    const activeThreadId = threadId || createThreadId();
    if (!threadId) {
      setThreadId(activeThreadId);
    }

    const turnId = nextTurnId();
    const sequence = requestRef.current;

    setTurns((current) => [
      ...current,
      { id: turnId, question: trimmed, state: "pending" },
    ]);
    setSelectedTurnId(turnId);
    setInput("");
    setBusy(true);

    try {
      const response = await client.sendChat({
        role: roleId,
        thread_id: activeThreadId,
        message: trimmed,
      });
      if (requestRef.current !== sequence) {
        return;
      }
      setTurns((current) =>
        current.map((turn) =>
          turn.id === turnId
            ? { id: turn.id, question: turn.question, state: "ready", response }
            : turn,
        ),
      );
    } catch (error) {
      if (requestRef.current !== sequence) {
        return;
      }
      const failure = describeFailure(error);
      setTurns((current) =>
        current.map((turn) =>
          turn.id === turnId
            ? {
                id: turn.id,
                question: turn.question,
                state: "failed",
                message: failure.message,
                code: failure.code,
              }
            : turn,
        ),
      );
    } finally {
      if (requestRef.current === sequence) {
        setBusy(false);
      }
    }
  }

  function previewScenario(scenario: (typeof contractFixtureScenarios)[number]) {
    if (busy) {
      return;
    }
    const turnId = nextTurnId();
    setTurns((current) => [
      ...current,
      {
        id: turnId,
        question: scenario.question,
        state: "ready",
        response: scenario.response,
      },
    ]);
    setSelectedTurnId(turnId);
    setSidebarOpen(false);
  }

  function retry(turn: Turn) {
    if (busy) {
      return;
    }
    setTurns((current) => current.filter((item) => item.id !== turn.id));
    void send(turn.question);
  }

  const selectedTurn = turns.find(
    (turn) => turn.id === selectedTurnId && turn.state === "ready",
  );
  const selectedResponse =
    selectedTurn && selectedTurn.state === "ready" ? selectedTurn.response : null;

  const lastReady = [...turns].reverse().find((turn) => turn.state === "ready");
  const liveMessage = busy
    ? "Waiting for a response"
    : lastReady && lastReady.state === "ready"
      ? `Response received. Status ${statusLabels[lastReady.response.status]}.`
      : "";

  return (
    <div
      className="app-shell"
      data-role={roleId}
      data-thread-id={threadId}
      data-fixtures={fixturesMode ? "contract" : "api"}
    >
      <p aria-live="polite" className="sr-only" role="status">
        {liveMessage}
      </p>

      <aside className={`sidebar ${sidebarOpen ? "sidebar-open" : ""}`}>
        <div className="brand">
          <div className="brand-mark" aria-hidden="true">
            <span />
            <span />
            <span />
          </div>
          <div>
            <strong>Factory Query</strong>
            <span>Data assistant</span>
          </div>
          <button
            aria-label="Close menu"
            className="close-menu"
            onClick={() => setSidebarOpen(false)}
            type="button"
          >
            <CloseIcon />
          </button>
        </div>

        <button className="new-chat" onClick={startFreshConversation} type="button">
          <PlusIcon size={17} />
          New conversation
        </button>

        {fixturesMode ? (
          <nav className="conversation-nav" aria-label="Contract fixtures">
            <p>Contract fixtures</p>
            {contractFixtureScenarios.map((scenario) => (
              <button
                disabled={busy}
                key={scenario.id}
                onClick={() => previewScenario(scenario)}
                type="button"
              >
                <span
                  className={`nav-status nav-${scenario.response.status}`}
                  aria-hidden="true"
                />
                <span>
                  <strong>{scenario.label}</strong>
                  <small>{scenario.id}</small>
                </span>
              </button>
            ))}
          </nav>
        ) : (
          <div className="sidebar-note">
            <InfoIcon size={15} />
            <p>Responses come from the configured backend contract.</p>
          </div>
        )}

        <div className="sidebar-footer">
          <div className="demo-pill">
            <span />
            DEMO ENVIRONMENT
          </div>
          <p>Fabricated sample data only. The role toggle is not authentication.</p>
        </div>
      </aside>

      {sidebarOpen ? (
        <button
          aria-label="Close menu"
          className="sidebar-scrim"
          onClick={() => setSidebarOpen(false)}
          type="button"
        />
      ) : null}

      <main className="main">
        <header className="topbar">
          <button
            aria-label="Open menu"
            className="menu-button"
            onClick={() => setSidebarOpen(true)}
            type="button"
          >
            <MenuIcon />
          </button>

          <div className="conversation-title">
            <div className="agent-avatar">
              <AgentIcon size={19} />
            </div>
            <div>
              <h1>Operations Q&amp;A</h1>
              <p>
                <span />
                {health
                  ? `Agent ready. Data profile: ${health.data_profile}.`
                  : "Agent ready."}
              </p>
            </div>
          </div>

          <div className="role-control">
            {fixturesMode ? (
              <span className="fixture-badge">CONTRACT FIXTURES</span>
            ) : null}
            <div className="role-label">
              <span>Viewing as</span>
              <strong>Demo role. Not authentication.</strong>
            </div>
            <RoleToggle
              activeRoleId={roleId}
              onSelect={switchRole}
              roles={roles}
            />
          </div>
        </header>

        <div className="workspace">
          <div className="chat-column">
            <div className="chat-scroll">
              <div className="chat-intro">
                <span className="intro-icon">
                  <ChatIcon size={21} />
                </span>
                <div>
                  <h2>Ask about your factory data</h2>
                  <p>
                    Questions are answered from the database only. When the data
                    cannot answer, the response says so.
                  </p>
                </div>
              </div>

              {rolesFailed ? (
                <div className="banner" role="alert">
                  <InfoIcon size={16} />
                  <p>
                    The role list could not be loaded. The contract role list is
                    shown until the backend responds.
                  </p>
                </div>
              ) : null}

              {turns.length === 0 ? (
                <div className="empty-conversation">
                  <div className="role-avatar">
                    {activeRole.label
                      .split(/\s+/)
                      .map((word) => word[0])
                      .join("")
                      .slice(0, 2)
                      .toUpperCase()}
                  </div>
                  <h2>{`New conversation for ${activeRole.label}`}</h2>
                  <p>
                    Switching roles always starts a new conversation. Ask a
                    question below
                    {fixturesMode
                      ? ", or open a contract fixture from the menu to preview every status."
                      : "."}
                  </p>
                </div>
              ) : null}

              {turns.map((turn) => (
                <div className="message-pair" key={turn.id}>
                  <div className="user-message">
                    <div className="user-avatar" aria-hidden="true">
                      {activeRole.label
                        .split(/\s+/)
                        .map((word) => word[0])
                        .join("")
                        .slice(0, 2)
                        .toUpperCase()}
                    </div>
                    <div>
                      <p>{turn.question}</p>
                      <span>{`You. Role: ${activeRole.label}`}</span>
                    </div>
                  </div>

                  {turn.state === "pending" ? (
                    <div className="agent-message">
                      <div className="mini-agent">
                        <AgentIcon size={15} />
                      </div>
                      <div className="thinking-card">
                        <div className="thinking-dots" aria-hidden="true">
                          <i />
                          <i />
                          <i />
                        </div>
                        <div>
                          <strong>Waiting for the backend</strong>
                          <span>No answer is rendered until the response arrives.</span>
                        </div>
                      </div>
                    </div>
                  ) : null}

                  {turn.state === "failed" ? (
                    <div className="agent-message">
                      <div className="mini-agent">
                        <AgentIcon size={15} />
                      </div>
                      <div className="transport-card" role="alert">
                        <div className="answer-topline">
                          <span className="status-badge status-error">Error</span>
                          {turn.code ? (
                            <span className="reason-code">{turn.code}</span>
                          ) : null}
                        </div>
                        <p className="answer-body">{turn.message}</p>
                        <button
                          className="retry-button"
                          onClick={() => retry(turn)}
                          type="button"
                        >
                          <RetryIcon size={15} />
                          Try again
                        </button>
                      </div>
                    </div>
                  ) : null}

                  {turn.state === "ready" ? (
                    <div className="agent-message">
                      <div className="mini-agent">
                        <AgentIcon size={15} />
                      </div>
                      <AnswerCard
                        onSelect={() => setSelectedTurnId(turn.id)}
                        question={turn.question}
                        response={turn.response}
                        selected={selectedTurnId === turn.id}
                      />
                    </div>
                  ) : null}
                </div>
              ))}

              <div ref={bottomRef} />
            </div>

            <Composer
              busy={busy}
              onChange={setInput}
              onSubmit={() => void send(input)}
              value={input}
            />
          </div>

          <aside className="evidence-panel" aria-label="Evidence">
            <EvidencePanel response={selectedResponse} />
          </aside>
        </div>
      </main>
    </div>
  );
}
