"""Deterministic leak scanner for chat response bodies.

Pure function over the full response body (payload, evidence, notes, errors)
implementing defense-in-depth role scanning and credential detection.
Authoritative source: docs/roles.md, PROJECT_SPEC.md (AT-06, AT-11, AT-13).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

# Forbidden column / field names for inventory_manager (case-insensitive match)
FORBIDDEN_MONETARY_FIELDS = {
    "price",
    "cost",
    "cost_price",
    "selling_price",
    "unit_price",
    "total_price",
    "amount",
    "sales_amount",
    "total_amount",
    "margin",
    "revenue",
    "total_revenue",
    "valuation",
    "stock_valuation",
    "inventory_value",
    "subtotal",
    "profit",
    "earnings",
    "spend",
    "reorder_cost",
    "restock_cost",
    "markup",
    "discount",
    "tier",
    "price_band",
    "pricing_tier",
    "grade",
}

# Regex patterns for currency amounts and symbols
CURRENCY_PATTERNS = [
    re.compile(r"[$€£¥₹]\s*\d+(?:\.\d+)?", re.IGNORECASE),
    re.compile(r"\b\d+(?:\.\d+)?\s*[$€£¥₹]", re.IGNORECASE),
    re.compile(r"\b(?:USD|EUR|GBP|INR)\s*\d+(?:\.\d+)?\b", re.IGNORECASE),
    re.compile(r"\b\d+(?:\.\d+)?\s*(?:USD|EUR|GBP|INR)\b", re.IGNORECASE),
]

# Qualitative price / monetary words forbidden in inventory_manager text
FORBIDDEN_TEXT_KEYWORDS = [
    "expensive",
    "cheap",
    "cheapest",
    "cheaper",
    "costly",
    "premium",
    "profit",
    "margin",
    "markup",
    "valuation",
    "revenue",
    "earnings",
    "capital tied up",
    "abc analysis",
    "inventory value",
    "total value",
    "restock cost",
    "reorder cost",
    "selling price",
    "unit price",
    "cost price",
    "most valuable",
    "top by revenue",
]

# Secret patterns forbidden for ALL roles
SECRET_PATTERNS = [
    (re.compile(r"sk-[a-zA-Z0-9_\-]{20,}", re.IGNORECASE), "openai_api_key"),
    (re.compile(r"postgres(?:ql)?://[^\s'\"`]+", re.IGNORECASE), "database_connection_url"),
    (re.compile(r"bearer\s+[a-zA-Z0-9_\-\.]{20,}", re.IGNORECASE), "bearer_token"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "private_key"),
    (
        re.compile(r"(?:OPENAI_API_KEY|DATABASE_URL)\s*=\s*[^\s'\"`]+", re.IGNORECASE),
        "env_secret_assignment",
    ),
]


@dataclass(frozen=True)
class Violation:
    path: str
    rule: str
    message: str
    matched_term: str


@dataclass(frozen=True)
class ScanResult:
    passed: bool
    violations: list[Violation]

    @property
    def is_safe(self) -> bool:
        return self.passed


def _normalize_response(response: Any) -> dict[str, Any]:
    """Convert Pydantic models or dicts into standard dict."""
    if hasattr(response, "model_dump"):
        dumped = response.model_dump()
        if isinstance(dumped, dict):
            return dumped
    if isinstance(response, dict):
        return response
    return {"raw_value": str(response)}


def _check_forbidden_key(key: str, path: str, violations: list[Violation]) -> None:
    """Check if a dictionary key / column name is a forbidden monetary field."""
    key_lower = key.lower().strip()
    tokens = set(re.split(r"[\s_\-]+", key_lower))
    if key_lower in FORBIDDEN_MONETARY_FIELDS or any(
        t in FORBIDDEN_MONETARY_FIELDS for t in tokens
    ):
        violations.append(
            Violation(
                path=path,
                rule="forbidden_monetary_field",
                message=f"Forbidden monetary field name '{key}' detected in response",
                matched_term=key,
            )
        )


def _check_monetary_text(text: str, path: str, violations: list[Violation]) -> None:
    """Check text for currency symbols, monetary figures, and forbidden language."""
    for pattern in CURRENCY_PATTERNS:
        match = pattern.search(text)
        if match:
            violations.append(
                Violation(
                    path=path,
                    rule="monetary_value",
                    message=f"Monetary value or currency symbol detected: '{match.group()}'",
                    matched_term=match.group(),
                )
            )

    text_lower = text.lower()

    # Check for forbidden hidden field names in text (e.g. price, cost, unit_price)
    for field_name in FORBIDDEN_MONETARY_FIELDS:
        pattern = r"\b" + re.escape(field_name) + r"\b"
        if re.search(pattern, text_lower):
            violations.append(
                Violation(
                    path=path,
                    rule="monetary_field_in_text",
                    message=f"Hidden monetary field name '{field_name}' revealed in text",
                    matched_term=field_name,
                )
            )

    # Check for qualitative price keywords
    for kw in FORBIDDEN_TEXT_KEYWORDS:
        pattern = r"\b" + re.escape(kw) + r"\b"
        if re.search(pattern, text_lower):
            violations.append(
                Violation(
                    path=path,
                    rule="monetary_keyword",
                    message=f"Forbidden monetary keyword detected: '{kw}'",
                    matched_term=kw,
                )
            )


def _check_secrets(text: str, path: str, violations: list[Violation]) -> None:
    """Check text for secret and credential leaks across all roles."""
    for pattern, rule_name in SECRET_PATTERNS:
        match = pattern.search(text)
        if match:
            violations.append(
                Violation(
                    path=path,
                    rule=f"secret_leak_{rule_name}",
                    message=f"Credential or secret pattern detected in response ({rule_name})",
                    matched_term=match.group()[:12] + "...",
                )
            )


def _walk_and_scan(
    obj: Any,
    path: str,
    role: str,
    violations: list[Violation],
) -> None:
    """Recursively walk any response structure scanning keys and values."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            current_path = f"{path}.{k}" if path else str(k)
            # Scan secrets in key names
            _check_secrets(str(k), f"{current_path}.__key__", violations)
            # Scan monetary keys if restricted role
            if role in ("inventory_manager", "purchase_manager"):
                _check_forbidden_key(str(k), current_path, violations)
            _walk_and_scan(v, current_path, role, violations)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            current_path = f"{path}[{i}]"
            _walk_and_scan(item, current_path, role, violations)
    elif isinstance(obj, str):
        # Scan secrets in all strings regardless of role
        _check_secrets(obj, path, violations)
        # Scan monetary values and keywords if restricted role
        if role in ("inventory_manager", "purchase_manager"):
            _check_monetary_text(obj, path, violations)
    elif isinstance(obj, (int, float)):
        pass


def scan_response(
    response: Any,
    role: str | None = None,
) -> ScanResult:
    """Scan a full response body for leaks, forbidden monetary terms, and secrets.

    Args:
        response: dict or Pydantic model representing the response body.
        role: the effective role for the response. If None, derived from response['role'].
              If role cannot be determined, defaults to 'inventory_manager' (deny-by-default).

    Returns:
        ScanResult with passed=True if clean, passed=False with list of Violations if leaks found.
    """
    data = _normalize_response(response)

    effective_role = role or data.get("role")
    if not effective_role:
        effective_role = "inventory_manager"

    violations: list[Violation] = []

    # 1. Structural recursive scan of all fields, payload, evidence, notes, errors
    _walk_and_scan(data, "", effective_role, violations)

    # 2. Specialized checks for presentation if present
    presentation = data.get("presentation")
    if isinstance(presentation, dict) and effective_role in (
        "inventory_manager",
        "purchase_manager",
    ):
        cols = presentation.get("columns", [])
        if isinstance(cols, list):
            for i, col in enumerate(cols):
                if isinstance(col, dict):
                    col_key = str(col.get("key", ""))
                    col_label = str(col.get("label", ""))
                    _check_forbidden_key(col_key, f"presentation.columns[{i}].key", violations)
                    _check_monetary_text(col_label, f"presentation.columns[{i}].label", violations)

        series_list = presentation.get("series", [])
        if isinstance(series_list, list):
            for i, s in enumerate(series_list):
                if isinstance(s, dict):
                    s_key = str(s.get("key", ""))
                    s_label = str(s.get("label", ""))
                    _check_forbidden_key(s_key, f"presentation.series[{i}].key", violations)
                    _check_monetary_text(s_label, f"presentation.series[{i}].label", violations)

    # 3. Specialized checks for evidence entries if present
    evidence = data.get("evidence", [])
    if isinstance(evidence, list) and effective_role in ("inventory_manager", "purchase_manager"):
        for i, ev in enumerate(evidence):
            if isinstance(ev, dict):
                cols = ev.get("columns", [])
                if isinstance(cols, list):
                    for c in cols:
                        _check_forbidden_key(str(c), f"evidence[{i}].columns", violations)

    return ScanResult(
        passed=len(violations) == 0,
        violations=violations,
    )


def is_response_safe(response: Any, role: str | None = None) -> bool:
    """Convenience boolean check for response safety."""
    return scan_response(response, role=role).passed
