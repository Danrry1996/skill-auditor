#!/usr/bin/env python3
"""Static auditor for agent skill/plugin repositories."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


TEXT_EXTENSIONS = {
    ".bash",
    ".bat",
    ".cmd",
    ".js",
    ".json",
    ".md",
    ".mjs",
    ".ps1",
    ".py",
    ".sh",
    ".toml",
    ".ts",
    ".txt",
    ".yaml",
    ".yml",
}

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build", "tests", "test"}
MAX_FILE_BYTES = 500_000


@dataclass(frozen=True)
class Rule:
    rule_id: str
    pattern: re.Pattern[str]
    severity: str
    points: int
    title: str
    recommendation: str


RULES = [
    Rule(
        "remote-shell-pipe",
        re.compile(r"\b(curl|wget|iwr|irm)\b[^\n|;&]*(https?://|raw\.githubusercontent)[^\n]*(\||;|&&)\s*(bash|sh|zsh|pwsh|powershell|python|node)\b", re.I),
        "critical",
        35,
        "Remote download is piped directly into an interpreter",
        "Require a pinned URL or checksum, download to a file first, inspect it, then execute only after explicit user approval.",
    ),
    Rule(
        "destructive-home-delete",
        re.compile(r"\brm\s+(-[^\n\s]*r[^\n\s]*f|-f[^\n\s]*r|-rf|-fr)\s+([~$%]|/|[A-Za-z]:\\)", re.I),
        "critical",
        35,
        "Recursive force deletion targets a broad home, root, or environment path",
        "Replace broad deletion with a resolved allowlisted path and a dry-run plus explicit confirmation.",
    ),
    Rule(
        "secret-exfiltration-risk",
        re.compile(r"(OPENAI_API_KEY|ANTHROPIC_API_KEY|GITHUB_TOKEN|GH_TOKEN|AWS_SECRET_ACCESS_KEY|id_rsa|\.ssh|process\.env|os\.environ|getenv)", re.I),  # skill-auditor: ignore
        "high",
        25,
        "Sensitive credentials or environment variables are accessed",
        "Explain why the secret is needed, redact logs, avoid printing environment state, and keep tokens in local secure storage.",
    ),
    Rule(
        "unsafe-permissions",
        re.compile(r"\b(chmod\s+(777|666)|icacls\b[^\n]*(Everyone|Users)[^\n]*(/grant|:F))", re.I),  # skill-auditor: ignore
        "high",
        20,
        "Overly broad filesystem permissions are granted",
        "Use least-privilege permissions on the narrowest path and document why the permission is required.",
    ),
    Rule(
        "untrusted-eval",
        re.compile(r"(\b(eval|exec)\s*\(|\bnew\s+Function\s*\(|\b(Invoke-Expression|iex)\b\s+)", re.I),
        "medium",
        12,
        "Dynamic code execution is present",
        "Avoid string evaluation; if unavoidable, constrain input and document the trust boundary.",
    ),
    Rule(
        "auto-global-install",
        re.compile(r"\b(npm\s+i(?:nstall)?\s+-g|pip\s+install\b|curl\b[^\n]*\|\s*npm|brew\s+install|choco\s+install)\b", re.I),
        "medium",
        10,
        "Install command may modify global user state",
        "Prefer local, pinned dependencies and ask before global installs.",
    ),
    Rule(
        "network-post",
        re.compile(r"\b(fetch|axios|requests\.post|curl\s+(-X\s+)?POST|Invoke-RestMethod)\b", re.I),  # skill-auditor: ignore
        "medium",
        10,
        "Outbound network transmission is possible",
        "Document what data leaves the machine, destination domains, and opt-out behavior.",
    ),
]


def iter_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if not path.is_file():
            continue
        if path.suffix.lower() not in TEXT_EXTENSIONS and path.name not in {"SKILL.md", "README"}:
            continue
        if path.stat().st_size > MAX_FILE_BYTES:
            continue
        yield path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def risk_level(score: int) -> str:
    if score >= 80:
        return "critical"
    if score >= 50:
        return "high"
    if score >= 25:
        return "medium"
    return "low"


def audit(root: Path) -> dict:
    if not root.exists():
        raise SystemExit(f"Target does not exist: {root}")

    findings = []
    files_scanned = 0
    for path in iter_files(root):
        files_scanned += 1
        text = read_text(path)
        rel = str(path.relative_to(root)).replace("\\", "/")
        for line_no, line in enumerate(text.splitlines(), 1):
            if "skill-auditor: ignore" in line:
                continue
            for rule in RULES:
                if rule.pattern.search(line):
                    findings.append(
                        {
                            "rule_id": rule.rule_id,
                            "severity": rule.severity,
                            "points": rule.points,
                            "title": rule.title,
                            "file": rel,
                            "line": line_no,
                            "evidence": line.strip()[:240],
                            "recommendation": rule.recommendation,
                        }
                    )

    score = min(sum(item["points"] for item in findings), 100)
    return {
        "target": str(root.resolve()),
        "summary": {
            "risk_level": risk_level(score),
            "score": score,
            "findings": len(findings),
            "files_scanned": files_scanned,
        },
        "findings": findings,
    }


def render_markdown(report: dict) -> str:
    summary = report["summary"]
    lines = [
        "# Skill Audit Report",
        "",
        f"- Target: `{report['target']}`",
        f"- Risk level: **{summary['risk_level']}**",
        f"- Score: **{summary['score']} / 100**",
        f"- Findings: **{summary['findings']}**",
        f"- Files scanned: **{summary['files_scanned']}**",
        "",
    ]
    if not report["findings"]:
        lines.append("No static risk findings were detected by the bundled rules.")
        return "\n".join(lines) + "\n"

    lines.append("## Findings")
    lines.append("")
    for item in report["findings"]:
        lines.extend(
            [
                f"### {item['severity'].upper()} - {item['title']}",
                "",
                f"- Rule: `{item['rule_id']}`",
                f"- Location: `{item['file']}:{item['line']}`",
                f"- Evidence: `{item['evidence']}`",
                f"- Recommendation: {item['recommendation']}",
                "",
            ]
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit an agent skill/plugin directory for static risk signals.")
    parser.add_argument("target", type=Path, help="Skill, plugin, or repository directory to audit")
    parser.add_argument("--json", action="store_true", help="Write machine-readable JSON")
    args = parser.parse_args()

    report = audit(args.target)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(render_markdown(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
