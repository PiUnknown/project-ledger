"""A deterministic API stub used until Lane B supplies the agent graph."""

from __future__ import annotations

from app.enforcement.interface import RoleExecutor
from app.roles.context import Role, RoleContext
from app.schemas import (
    ChatResponse,
    TablePresentation,
    TextPresentation,
)


class StubAgent:
    """Answer one explicit demo command and clarify other requests."""

    def run(
        self,
        *,
        message: str,
        context: RoleContext,
        thread_id: str,
        request_id: str,
        executor: RoleExecutor,
        row_limit: int,
        timeout_ms: int,
    ) -> ChatResponse:
        if context.role is Role.PURCHASE_MANAGER:
            return ChatResponse(
                contract_version="0.1",
                request_id=request_id,
                role=context.role.value,
                thread_id=thread_id,
                status="refused",
                reason_code="role_not_configured",
                answer_text="This role is not configured.",
                presentation=TextPresentation(type="text"),
                evidence=[],
                notes=[],
            )

        command = " ".join(message.lower().split())
        if command in {"list sample items", "show sample items", "show demo items"}:
            result = executor.execute(
                context,
                "list_sample_items",
                {},
                row_limit=row_limit,
                timeout_ms=timeout_ms,
            )
            if not result.rows:
                return ChatResponse(
                    contract_version="0.1",
                    request_id=request_id,
                    role=context.role.value,
                    thread_id=thread_id,
                    status="no_data",
                    reason_code="data_not_available",
                    answer_text="The fabricated sample has no matching items.",
                    presentation=TextPresentation(type="text"),
                    evidence=[result.evidence],
                    notes=[],
                )
            return ChatResponse(
                contract_version="0.1",
                request_id=request_id,
                role=context.role.value,
                thread_id=thread_id,
                status="answered",
                reason_code=None,
                answer_text="These are the fabricated sample items.",
                presentation=TablePresentation(
                    type="table",
                    columns=list(result.columns),
                    rows=list(result.rows),
                    total_rows=result.total_rows,
                    truncated=result.truncated,
                ),
                evidence=[result.evidence],
                notes=[],
            )

        return ChatResponse(
            contract_version="0.1",
            request_id=request_id,
            role=context.role.value,
            thread_id=thread_id,
            status="needs_clarification",
            reason_code="ambiguous_entity",
            answer_text="Please clarify which item or inventory detail you want to check.",
            presentation=TextPresentation(type="text"),
            evidence=[],
            notes=[],
        )
