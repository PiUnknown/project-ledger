"""FastAPI application and v0.1 endpoints."""

from __future__ import annotations

from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.agent_stub import StubAgent
from app.api.chat import router as chat_router
from app.api.errors import APIError
from app.config import Settings
from app.enforcement.interface import RoleExecutor
from app.enforcement.mock_executor import build_mock_executor
from app.limits.limiter import RequestLimiter
from app.schemas import ErrorResponse, HealthResponse, RoleSummary


def create_app(
    settings: Settings | None = None,
    *,
    executor: RoleExecutor | None = None,
    agent: StubAgent | None = None,
    limiter: RequestLimiter | None = None,
) -> FastAPI:
    active_settings = settings or Settings.from_env()
    app = FastAPI(title="Factory Item Agent API", version="0.1")
    app.state.settings = active_settings
    app.state.executor = executor or build_mock_executor()
    app.state.agent = agent or StubAgent()
    app.state.limiter = limiter or RequestLimiter(
        active_settings.rate_limit_per_minute,
        active_settings.daily_request_cap,
    )

    @app.middleware("http")
    async def attach_request_id(request: Request, call_next):
        request.state.request_id = str(uuid4())
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        return response

    @app.exception_handler(APIError)
    async def api_error_handler(request: Request, error: APIError) -> JSONResponse:
        payload = ErrorResponse(
            error={
                "code": error.code,
                "message": error.message,
                "request_id": getattr(request.state, "request_id", str(uuid4())),
            }
        )
        return JSONResponse(status_code=error.status_code, content=payload.model_dump(mode="json"))

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, error: RequestValidationError
    ) -> JSONResponse:
        payload = ErrorResponse(
            error={
                "code": "validation_error",
                "message": "The request does not match the API contract.",
                "request_id": getattr(request.state, "request_id", str(uuid4())),
            }
        )
        return JSONResponse(status_code=422, content=payload.model_dump(mode="json"))

    @app.get("/api/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        return HealthResponse(
            status="ok",
            contract_version="0.1",
            data_profile=active_settings.data_profile,
        )

    @app.get("/api/roles", response_model=list[RoleSummary])
    async def roles() -> list[RoleSummary]:
        return [
            RoleSummary(
                id="owner",
                label="Business Owner",
                description="Demo role with broad read access.",
                configured=True,
            ),
            RoleSummary(
                id="inventory_manager",
                label="Inventory Manager",
                description="Demo role for inventory questions.",
                configured=True,
            ),
            RoleSummary(
                id="purchase_manager",
                label="Purchase Manager",
                description="Access is not configured.",
                configured=False,
            ),
        ]

    app.include_router(chat_router, prefix="/api")
    return app


app = create_app()
