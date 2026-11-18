import {
  contractHealth,
  contractRoles,
  resolveFixtureResponse,
} from "./fixtures";
import {
  isApiErrorEnvelope,
  type ChatRequest,
  type ChatResponse,
  type HealthResponse,
  type RoleSummary,
} from "./types";

/**
 * The single data access point for the UI. Two implementations exist:
 * - HttpChatClient talks to the backend defined in docs/api.md.
 * - FixtureChatClient serves the contract fixtures in lib/fixtures.ts.
 *
 * Components never talk to a transport directly, so swapping fixtures for the
 * contract fixtures or the live API does not change any renderer.
 */
export interface ChatClient {
  listRoles(): Promise<RoleSummary[]>;
  getHealth(): Promise<HealthResponse | null>;
  sendChat(request: ChatRequest): Promise<ChatResponse>;
}

export class ApiRequestError extends Error {
  readonly code: string | null;
  readonly requestId: string | null;
  readonly httpStatus: number;

  constructor(options: {
    message: string;
    code: string | null;
    requestId: string | null;
    httpStatus: number;
  }) {
    super(options.message);
    this.name = "ApiRequestError";
    this.code = options.code;
    this.requestId = options.requestId;
    this.httpStatus = options.httpStatus;
  }
}

function normalizeBaseUrl(value: string | undefined): string | null {
  const trimmed = value?.trim();
  if (!trimmed) {
    return null;
  }
  return trimmed.replace(/\/+$/, "");
}

async function readErrorEnvelope(response: Response): Promise<ApiRequestError> {
  let body: unknown = null;
  try {
    body = await response.json();
  } catch {
    body = null;
  }

  if (isApiErrorEnvelope(body)) {
    return new ApiRequestError({
      message: body.error.message,
      code: body.error.code,
      requestId: body.error.request_id,
      httpStatus: response.status,
    });
  }

  return new ApiRequestError({
    message: "The server returned an error response without a contract error body.",
    code: null,
    requestId: null,
    httpStatus: response.status,
  });
}

export class HttpChatClient implements ChatClient {
  private readonly baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async listRoles(): Promise<RoleSummary[]> {
    const response = await fetch(`${this.baseUrl}/api/roles`, {
      method: "GET",
      headers: { Accept: "application/json" },
    });
    if (!response.ok) {
      throw await readErrorEnvelope(response);
    }
    return (await response.json()) as RoleSummary[];
  }

  async getHealth(): Promise<HealthResponse | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/health`, {
        method: "GET",
        headers: { Accept: "application/json" },
      });
      if (!response.ok) {
        return null;
      }
      return (await response.json()) as HealthResponse;
    } catch {
      return null;
    }
  }

  async sendChat(request: ChatRequest): Promise<ChatResponse> {
    const response = await fetch(`${this.baseUrl}/api/chat`, {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
    });
    if (!response.ok) {
      throw await readErrorEnvelope(response);
    }
    return (await response.json()) as ChatResponse;
  }
}

export class FixtureChatClient implements ChatClient {
  private readonly delayMs: number;

  constructor(delayMs = 0) {
    this.delayMs = delayMs;
  }

  async listRoles(): Promise<RoleSummary[]> {
    return contractRoles;
  }

  async getHealth(): Promise<HealthResponse | null> {
    return contractHealth;
  }

  async sendChat(request: ChatRequest): Promise<ChatResponse> {
    if (this.delayMs > 0) {
      await new Promise((resolve) => setTimeout(resolve, this.delayMs));
    }
    return resolveFixtureResponse(request);
  }
}

const apiBaseUrl = normalizeBaseUrl(process.env.NEXT_PUBLIC_API_BASE_URL);

/** True while the UI is driven by the contract fixtures. */
export function usingFixtureResponses(): boolean {
  return apiBaseUrl === null;
}

/** Backend when NEXT_PUBLIC_API_BASE_URL is set, contract fixtures otherwise. */
export function createChatClient(): ChatClient {
  if (apiBaseUrl) {
    return new HttpChatClient(apiBaseUrl);
  }
  return new FixtureChatClient(350);
}
