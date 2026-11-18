"""Live API Evaluation Runner.

Clearly marked entry point for executing probe cases and security evaluations
against a running FastAPI instance.

When no live API is reachable, reports NOT RUN - NO LIVE API.
Modules and imports are collection-safe for pytest.
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass, field
from typing import Any

from backend.app.guard.scanner import scan_response
from evals.cases.probes import ALL_PROBE_CASES, ProbeCase


@dataclass
class ProbeResult:
    case: ProbeCase
    status: str  # "PASSED", "FAILED", "BLOCKED_GATE_G1", "NOT_RUN"
    details: str = ""
    response_data: dict[str, Any] | None = None


@dataclass
class EvalRunSummary:
    status: str  # "PASSED", "FAILED", "NOT_RUN"
    message: str
    total_cases: int = 0
    passed: int = 0
    failed: int = 0
    blocked_gate_g1: int = 0
    not_run: int = 0
    results: list[ProbeResult] = field(default_factory=list)


def check_api_health(base_url: str) -> bool:
    """Check if the target API is live and responding."""
    try:
        import urllib.error
        import urllib.request

        health_url = f"{base_url.rstrip('/')}/api/health"
        req = urllib.request.Request(health_url, headers={"User-Agent": "EvalRunner/0.1"})
        with urllib.request.urlopen(req, timeout=2.0) as resp:
            return resp.status == 200
    except (OSError, urllib.error.URLError):
        return False


def run_evals(
    api_base_url: str | None = None,
    role: str = "all",
) -> EvalRunSummary:
    """Run probe evaluations against the live API.

    Entry point is strictly guarded: if no live API URL is provided or reachable,
    reports NOT RUN - NO LIVE API rather than failing.
    """
    target_url = api_base_url or os.environ.get("EVAL_API_BASE_URL")

    # If no URL or server unreachable, report NOT RUN - NO LIVE API
    if not target_url or not check_api_health(target_url):
        msg = (
            "NOT RUN - NO LIVE API: Target API is not configured or not reachable. "
            "Integration probes deferred until live backend is running."
        )
        print(f"\n[EVALS] {msg}\n")
        return EvalRunSummary(
            status="NOT_RUN",
            message=msg,
            total_cases=len(ALL_PROBE_CASES),
            not_run=len(ALL_PROBE_CASES),
        )

    # Filter cases by role
    selected_cases = [
        c for c in ALL_PROBE_CASES
        if role == "all" or c.role == role
    ]

    summary = EvalRunSummary(
        status="PASSED",
        message="Live API evaluation completed",
        total_cases=len(selected_cases),
    )

    import json
    import urllib.request
    import uuid

    for case in selected_cases:
        # Schema-dependent cases stay blocked until gate G1
        if case.is_schema_dependent:
            summary.blocked_gate_g1 += 1
            summary.results.append(
                ProbeResult(
                    case=case,
                    status="BLOCKED_GATE_G1",
                    details="Schema-dependent probe blocked until gate G1 schema inspection",
                )
            )
            continue

        payload = {
            "role": case.role,
            "thread_id": f"eval-{uuid.uuid4().hex[:12]}",
            "message": case.question,
        }

        try:
            chat_url = f"{target_url.rstrip('/')}/api/chat"
            req = urllib.request.Request(
                chat_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=5.0) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))

            # 1. Verify status
            actual_status = resp_data.get("status")
            if actual_status != case.expected_status:
                summary.failed += 1
                summary.status = "FAILED"
                summary.results.append(
                    ProbeResult(
                        case=case,
                        status="FAILED",
                        details=f"Expected status '{case.expected_status}', got '{actual_status}'",
                        response_data=resp_data,
                    )
                )
                continue

            # 2. Verify reason_code if specified
            if (
                case.expected_reason_code
                and resp_data.get("reason_code") != case.expected_reason_code
            ):
                summary.failed += 1
                summary.status = "FAILED"
                summary.results.append(
                    ProbeResult(
                        case=case,
                        status="FAILED",
                        details=(
                            f"Expected reason '{case.expected_reason_code}', "
                            f"got '{resp_data.get('reason_code')}'"
                        ),
                        response_data=resp_data,
                    )
                )
                continue

            # 3. Guard scan for leaks and forbidden strings
            scan = scan_response(resp_data, role=case.role)
            if not scan.passed:
                summary.failed += 1
                summary.status = "FAILED"
                summary.results.append(
                    ProbeResult(
                        case=case,
                        status="FAILED",
                        details=f"Guard scan detected leaks: {[v.message for v in scan.violations]}",
                        response_data=resp_data,
                    )
                )
                continue

            summary.passed += 1
            summary.results.append(
                ProbeResult(case=case, status="PASSED", response_data=resp_data)
            )

        except Exception as exc:  # noqa: BLE001
            summary.failed += 1
            summary.status = "FAILED"
            summary.results.append(
                ProbeResult(case=case, status="FAILED", details=f"HTTP/Network error: {exc}")
            )

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Live API Eval Runner")
    parser.add_argument("--url", default=None, help="Base URL of running API")
    parser.add_argument(
        "--role",
        default="all",
        choices=["all", "owner", "inventory_manager", "purchase_manager"],
    )
    args = parser.parse_args()

    summary = run_evals(api_base_url=args.url, role=args.role)
    print(
        f"Summary: Status={summary.status}, Total={summary.total_cases}, "
        f"Passed={summary.passed}, Failed={summary.failed}, "
        f"Blocked(G1)={summary.blocked_gate_g1}, NotRun={summary.not_run}"
    )
    if summary.status == "FAILED":
        sys.exit(1)


if __name__ == "__main__":
    main()
