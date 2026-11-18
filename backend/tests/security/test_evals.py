"""Unit tests for the eval harness, cases, secret scan, and live runner guard.

Verifies:
1. All eval cases conform to the required tuple schema and cover docs/roles.md.
2. Adversarial executor-bypass cases (AT-11) are well-formed.
3. Secret scanner (AT-13) passes cleanly on the repository.
4. Eval runner safely reports 'NOT RUN - NO LIVE API' when no server is present.
"""

from __future__ import annotations

from pathlib import Path

from evals.cases.adversarial import ADVERSARIAL_CASES, run_adversarial_simulation
from evals.cases.probes import (
    ALL_PROBE_CASES,
    INDIRECT_PROBES,
    get_all_probes,
    get_schema_dependent_probes,
    get_schema_independent_probes,
)
from evals.cases.secret_scan import run_repo_secret_scan
from evals.runner import run_evals


class TestProbeCasesSchema:
    def test_all_probes_conform_to_tuple_structure(self):
        tuples = get_all_probes()
        assert len(tuples) > 0
        for item in tuples:
            assert len(item) == 4
            role, question, expected_status, forbidden = item
            assert role in ("owner", "inventory_manager", "purchase_manager")
            assert len(question) > 0
            assert expected_status in ("answered", "refused", "no_data", "needs_clarification")
            assert isinstance(forbidden, list)

    def test_indirect_probes_cover_roles_doc(self):
        """Verify indirect probes mentioned in docs/roles.md line 21-28 are present."""
        questions_lower = [p.question.lower() for p in INDIRECT_PROBES]
        # Check presence of specific required probes:
        # 1. earnings if all sold
        assert any("earn" in q for q in questions_lower)
        # 2. ranking by value
        assert any("rank" in q and "value" in q for q in questions_lower)
        # 3. filtering by price threshold
        assert any("priced over" in q or "price" in q for q in questions_lower)
        # 4. total inventory value
        assert any("total" in q and "value" in q for q in questions_lower)
        # 5. ABC analysis by value
        assert any("abc" in q for q in questions_lower)
        # 6. average price per category
        assert any("average price" in q for q in questions_lower)
        # 7. restock cost
        assert any("restock cost" in q for q in questions_lower)

    def test_schema_gating_separation(self):
        dep = get_schema_dependent_probes()
        indep = get_schema_independent_probes()
        assert len(dep) > 0
        assert len(indep) > 0
        assert len(dep) + len(indep) == len(ALL_PROBE_CASES)


class TestAdversarialCases:
    def test_adversarial_cases_defined(self):
        assert len(ADVERSARIAL_CASES) >= 8
        case_ids = {c.case_id for c in ADVERSARIAL_CASES}
        assert len(case_ids) == len(ADVERSARIAL_CASES)  # All unique

    def test_adversarial_simulation_without_executor(self):
        sim = run_adversarial_simulation(None)
        assert sim["status"] == "READY_FOR_INTEGRATION"
        assert sim["total_cases"] == len(ADVERSARIAL_CASES)


class TestSecretScanner:
    def test_at13_secret_scan_passes_on_workspace(self):
        repo_root = Path(__file__).resolve().parent.parent.parent.parent
        result = run_repo_secret_scan(repo_root)
        assert result.gitignore_valid is True, f"Gitignore validation failed: {result.errors}"
        assert result.env_examples_valid is True, f"Env examples validation failed: {result.errors}"
        assert len(result.findings) == 0, f"Found secrets in repository: {result.findings}"
        assert result.passed is True


class TestEvalRunnerSafety:
    def test_runner_reports_not_run_when_no_api(self):
        """Runner must report NOT RUN - NO LIVE API rather than failing when server is absent."""
        summary = run_evals(api_base_url="http://127.0.0.1:9999")
        assert summary.status == "NOT_RUN"
        assert "NOT RUN - NO LIVE API" in summary.message
        assert summary.not_run == len(ALL_PROBE_CASES)
        assert summary.failed == 0
        assert summary.passed == 0
