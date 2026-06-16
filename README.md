# Skill Auditor

[![Agent Skill](https://img.shields.io/badge/agent-skill-0ea5e9)](SKILL.md)
[![Python](https://img.shields.io/badge/python-3.9%2B-3776ab)](scripts/audit_skill.py)
[![License: MIT](https://img.shields.io/badge/license-MIT-111827)](LICENSE)

[English](README.md) | [简体中文](README.zh-CN.md)

![Skill Auditor hero](assets/skill-auditor-hero.png)

**Audit third-party agent skills before you install them.**

`skill-auditor` is a Codex/Claude-style agent skill plus a local static scanner for reviewing skills, plugins, install scripts, and MCP-adjacent bundles. It helps an agent answer the question that matters before installation:

> Can I trust this skill enough to run it on my machine?

## Why This Exists

Agent skills are powerful because they combine instructions, scripts, dependencies, and local file access. That also makes them a supply-chain surface. A polished README, lots of stars, or a familiar author does not prove a skill is safe.

`skill-auditor` gives your agent a repeatable review workflow:

- inspect the `SKILL.md` instructions
- scan scripts and manifests for static risk signals
- review credential, filesystem, network, and install behavior
- produce an install verdict with file/line evidence
- recommend sandboxing or patches before trust is granted

## Quick Start

Clone this repository into your agent's skills folder.

For Codex-style skills:

```bash
git clone https://github.com/Danrry1996/skill-auditor.git ~/.codex/skills/skill-auditor
```

For Claude Code-style skills:

```bash
git clone https://github.com/Danrry1996/skill-auditor.git ~/.claude/skills/skill-auditor
```

On Windows PowerShell:

```powershell
git clone https://github.com/Danrry1996/skill-auditor.git "$env:USERPROFILE\.codex\skills\skill-auditor"
```

If your agent uses a different skills directory, clone the repository there. The repository root contains `SKILL.md`.

Then ask your agent:

```text
Use $skill-auditor to review this skill before I install it: <path-or-url>
```

## Run the Scanner Directly

The bundled scanner is dependency-free Python. It only reads files; it does not execute the target repository.

```bash
python scripts/audit_skill.py ./some-skill
python scripts/audit_skill.py ./some-skill --json > audit-report.json
```

Example output:

```text
# Skill Audit Report

- Risk level: high
- Score: 55 / 100
- Findings: 3

### CRITICAL - Remote download is piped directly into an interpreter
- Rule: remote-shell-pipe
- Location: scripts/install.sh:12
- Recommendation: Download to a file first, inspect it, and execute only after explicit approval.
```

## What It Checks

| Area | Examples |
| --- | --- |
| Remote execution | network downloads piped into shells or interpreters |
| Destructive actions | recursive force deletes, broad cleanup commands, unsafe path handling |
| Secrets | API keys, token stores, private keys, full environment dumps |
| Permissions | world-writable files, admin/root guidance, broad ACL changes |
| Network behavior | outbound posts, telemetry, file uploads, unclear domains |
| Dependencies | global installs, unpinned packages, moving branches, lifecycle scripts |
| Agent instructions | hidden trust requests, approval bypasses, vague data handling |

## Verdicts

`skill-auditor` guides the agent toward one of four outcomes:

| Verdict | Meaning |
| --- | --- |
| `install` | No meaningful static findings; scope is clear and limited. |
| `install with sandbox` | Useful, but it touches network, package managers, or broad local state. |
| `patch first` | Risk is fixable: pin dependencies, add confirmations, redact logs, narrow paths. |
| `reject` | Secret exfiltration, concealed remote execution, broad destructive actions, or approval bypasses. |

## Suggested Agent Prompt

```text
Use $skill-auditor to audit this repository before installation:
https://github.com/example/suspicious-skill

Give me a verdict, top risks, file/line evidence, and what I should change before installing.
```

## Repository Layout

```text
skill-auditor/
  SKILL.md                    # Agent workflow
  scripts/audit_skill.py       # Static scanner
  references/risk-rules.md     # Severity guide and manual review prompts
  agents/openai.yaml           # Codex UI metadata
  tests/                       # Scanner tests
  assets/                      # README visual assets
```

## Design Principles

- **Read before running.** Never execute a third-party installer just to learn what it does.
- **Evidence over vibes.** Every serious risk should point to a file and line.
- **Static first, human review second.** A scanner can focus attention; it cannot prove safety.
- **Least privilege by default.** Network, secrets, global installs, and broad filesystem access need justification.
- **Sandbox when uncertain.** Useful skills with unclear behavior belong in disposable environments first.

## Limits

This project is not a malware detector and cannot prove a repository is safe. It catches common static risk patterns and gives an agent a disciplined review process. A clean scan still requires human judgment.

## Development

Run tests:

```bash
python -m unittest discover -s tests
```

Validate the skill metadata with your local skill validator if available:

```bash
python path/to/quick_validate.py ./skill-auditor
```

Run a self-audit:

```bash
python scripts/audit_skill.py .
```

## Roadmap

**1. Core Audit Experience**

- [x] Agent workflow for `install`, `install with sandbox`, `patch first`, and `reject` verdicts.
- [x] Local static scanner with Markdown and JSON output.
- [x] File/line evidence for every static finding.
- [x] Built-in risk rule reference for manual review.
- [ ] Configurable allowlist for trusted internal domains.

**2. Automation Integrations**

- [ ] GitHub Action for pull request audit comments.
- [ ] SARIF output for code scanning integrations.
- [ ] CI-friendly exit codes and risk thresholds.
- [ ] Machine-readable configuration for rule tuning.

**3. Deeper Security Coverage**

- [ ] Stronger manifest and lifecycle-script parsing.
- [ ] Richer MCP/server permission review.
- [ ] Dependency pinning and checksum checks.
- [ ] Sandbox install recipe generation.

## License

MIT
