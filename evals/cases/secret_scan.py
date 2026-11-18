"""Repository secret scanner (PROJECT_SPEC AT-13).

Scans workspace files, gitignore rules, and example configuration files to verify:
1. No credentials, tokens, or private keys exist in the repository.
2. Secret env files (.env, .env.local) and .doclock are ignored by git.
3. Env example files (.env.example, .env.local.example) are preserved and contain no secrets.
4. Frontend configuration contains no backend secrets.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import NamedTuple

# File / directory exclusions from recursive secret walk
EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".next",
}

# Suspicious credential patterns
CREDENTIAL_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"sk-[a-zA-Z0-9_\-]{20,}", re.IGNORECASE), "openai_api_key"),
    (
        re.compile(r"postgres(?:ql)?://[^:\s]+:[^@\s]+@[^\s'\"`]+", re.IGNORECASE),
        "db_url_with_credentials",
    ),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "private_key"),
    (re.compile(r"bearer\s+eyJ[a-zA-Z0-9_\-\.]{20,}", re.IGNORECASE), "jwt_bearer_token"),
    (re.compile(r"(?:ghp|gho|ghu|ghs|ghr)_[a-zA-Z0-9]{36,}", re.IGNORECASE), "github_token"),
]


class SecretFinding(NamedTuple):
    file_path: str
    pattern_type: str
    line_number: int
    snippet: str


class SecretScanResult(NamedTuple):
    passed: bool
    findings: list[SecretFinding]
    gitignore_valid: bool
    env_examples_valid: bool
    errors: list[str]


def scan_file_for_credentials(file_path: Path) -> list[SecretFinding]:
    """Scan a single text file for hardcoded credentials."""
    findings: list[SecretFinding] = []
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return findings

    for line_idx, line in enumerate(content.splitlines(), start=1):
        for pattern, pattern_name in CREDENTIAL_PATTERNS:
            match = pattern.search(line)
            if match:
                findings.append(
                    SecretFinding(
                        file_path=str(file_path),
                        pattern_type=pattern_name,
                        line_number=line_idx,
                        snippet=line[:100],
                    )
                )
    return findings


def verify_gitignore(repo_root: Path) -> tuple[bool, list[str]]:
    """Verify that .gitignore ignores secret env files and .doclock while preserving examples."""
    gitignore_path = repo_root / ".gitignore"
    if not gitignore_path.is_file():
        return False, ["Missing .gitignore in repo root"]

    content = gitignore_path.read_text(encoding="utf-8", errors="ignore")
    lines = [
        line.strip()
        for line in content.splitlines()
        if line.strip() and not line.startswith("#")
    ]

    errors: list[str] = []

    # Check that .env or .env* is ignored
    if not any(pattern in lines for pattern in [".env", ".env.*"]):
        errors.append(".gitignore must ignore .env and .env.*")

    # Check that .doclock is ignored
    if ".doclock" not in lines:
        errors.append(".gitignore must ignore .doclock")

    # Check that env examples are explicitly preserved
    if "!.env.example" not in lines:
        errors.append(".gitignore must preserve !.env.example")
    if "!.env.local.example" not in lines:
        errors.append(".gitignore must preserve !.env.local.example")

    return len(errors) == 0, errors


def verify_env_examples(repo_root: Path) -> tuple[bool, list[str]]:
    """Verify that .env.example files contain no secrets or populated values."""
    errors: list[str] = []

    backend_example = repo_root / "backend" / ".env.example"
    frontend_example = repo_root / "frontend" / ".env.local.example"

    if backend_example.is_file():
        content = backend_example.read_text(encoding="utf-8", errors="ignore")
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                val = val.strip()
                # Default non-secret values like 'local', 'fabricated', 'false', '0.1' are allowed;
                # actual credentials (API keys, passwords) must be empty.
                if key.strip() in ("OPENAI_API_KEY", "DATABASE_URL", "LANGSMITH_API_KEY") and val:
                    errors.append(f"backend/.env.example must have empty value for {key}")

    if frontend_example.is_file():
        content = frontend_example.read_text(encoding="utf-8", errors="ignore")
        forbidden_frontend_keys = [
            "DATABASE_URL",
            "DATABASE_URL_OWNER",
            "OPENAI_API_KEY",
            "LANGSMITH_API_KEY",
        ]
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key = line.split("=", 1)[0].strip()
                if key in forbidden_frontend_keys:
                    errors.append(f"frontend/.env.local.example must never contain {key}")

    return len(errors) == 0, errors


def run_repo_secret_scan(repo_root: Path | None = None) -> SecretScanResult:
    """Run full repository secret scan according to AT-13 rules."""
    root = repo_root or Path(__file__).resolve().parent.parent.parent

    findings: list[SecretFinding] = []
    errors: list[str] = []

    # 1. Walk workspace files
    for current_dir, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for f in files:
            file_path = Path(current_dir) / f
            findings.extend(scan_file_for_credentials(file_path))

    # 2. Verify gitignore
    gi_valid, gi_errors = verify_gitignore(root)
    errors.extend(gi_errors)

    # 3. Verify env examples
    env_valid, env_errors = verify_env_examples(root)
    errors.extend(env_errors)

    passed = len(findings) == 0 and gi_valid and env_valid
    return SecretScanResult(
        passed=passed,
        findings=findings,
        gitignore_valid=gi_valid,
        env_examples_valid=env_valid,
        errors=errors,
    )
