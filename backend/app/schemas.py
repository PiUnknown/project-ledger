"""Pydantic models mirroring API contract v0.1 in docs/api.md."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any, Literal, Union

from pydantic import BaseModel, ConfigDict, Field, model_validator

RoleName = Literal["owner", "inventory_manager", "purchase_manager"]
ResponseStatus = Literal["answered", "refused", "no_data", "needs_clarification", "error"]
ReasonCode = Literal[
    "outside_role_access",
    "role_not_configured",
    "unsupported_request",
    "data_not_available",
    "ambiguous_entity",
]
ValueType = Literal["string", "number", "integer", "date", "boolean"]
ChartValueType = Literal["string", "number", "integer", "date"]
EvidenceKind = Literal["tool", "sql_view"]
JsonRow = dict[str, Any]


class ContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class HealthResponse(ContractModel):
    status: Literal["ok"]
    contract_version: Literal["0.1"]
    data_profile: Literal["private", "fabricated"]


class RoleSummary(ContractModel):
    id: RoleName
    label: str
    description: str
    configured: bool


class ChatRequest(ContractModel):
    role: str
    thread_id: str = Field(min_length=8, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")
    message: str = Field(min_length=1, max_length=2000)


class TextPresentation(ContractModel):
    type: Literal["text"]


class TableColumn(ContractModel):
    key: str
    label: str
    type: ValueType


class TablePresentation(ContractModel):
    type: Literal["table"]
    columns: list[TableColumn]
    rows: list[JsonRow]
    total_rows: int = Field(ge=0)
    truncated: bool


class ChartAxis(ContractModel):
    key: str
    label: str
    type: ChartValueType


class ChartSeries(ContractModel):
    key: str
    label: str


class ChartPresentation(ContractModel):
    type: Literal["chart"]
    kind: Literal["bar", "line"]
    title: str
    x: ChartAxis
    series: list[ChartSeries]
    rows: list[JsonRow]
    truncated: bool


Presentation = Annotated[
    Union[TextPresentation, TablePresentation, ChartPresentation],
    Field(discriminator="type"),
]


class EvidenceEntry(ContractModel):
    id: str
    kind: EvidenceKind
    label: str
    detail: str
    columns: list[str]
    row_count: int = Field(ge=0)
    rows_preview: list[JsonRow]
    executed_at: datetime


class ChatResponse(ContractModel):
    contract_version: Literal["0.1"]
    request_id: str
    role: RoleName
    thread_id: str
    status: ResponseStatus
    reason_code: ReasonCode | None
    answer_text: str
    presentation: Presentation
    evidence: list[EvidenceEntry]
    notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_status_fields(self) -> ChatResponse:
        if self.status == "answered":
            if self.reason_code is not None:
                raise ValueError("answered responses must have a null reason_code")
            if not self.evidence:
                raise ValueError("answered responses require evidence")
        elif self.reason_code is None:
            raise ValueError("non-answered responses require a reason_code")
        return self


class ErrorDetail(ContractModel):
    code: str
    message: str
    request_id: str


class ErrorResponse(ContractModel):
    error: ErrorDetail
