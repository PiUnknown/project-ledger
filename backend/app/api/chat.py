"""Chat request validation, role isolation, limits and agent dispatch."""

from __future__ import annotations

from fastapi import APIRouter, Request

from app.api.errors import APIError
from app.enforcement.interface import QueryTimeout
from app.roles.context import InvalidRole, RoleContext
from app.schemas import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest, request: Request) -> ChatResponse:
    request_id: str = request.state.request_id
    try:
        context = RoleContext.from_request(body.role)
    except InvalidRole as error:
        raise APIError(422, "invalid_role", "The requested role is not available.") from error

    client = request.client
    ip_address = client.host if client is not None else "unknown"
    limit_code = request.app.state.limiter.consume(ip_address)
    if limit_code == "rate_limited":
        raise APIError(429, limit_code, "The request rate limit has been reached.")
    if limit_code == "daily_cap_reached":
        raise APIError(429, limit_code, "The daily request cap has been reached.")

    effective_thread_id = context.effective_thread_id(body.thread_id)
    try:
        return request.app.state.agent.run(
            message=body.message,
            context=context,
            thread_id=effective_thread_id,
            request_id=request_id,
            executor=request.app.state.executor,
            row_limit=request.app.state.settings.query_row_limit,
            timeout_ms=request.app.state.settings.query_timeout_ms,
        )
    except QueryTimeout as error:
        raise APIError(
            504,
            "query_timeout",
            "The request exceeded the allowed query time.",
        ) from error
    except Exception as error:
        raise APIError(500, "internal_error", "The request could not be completed.") from error
