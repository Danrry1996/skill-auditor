---
name: skill-auditor
description: Use when reviewing third-party agent skills, Claude Code plugins, Codex skills, MCP-adjacent bundles, install scripts, SKILL.md files, or copied skill repositories before installing, updating, publishing, or recommending them.
---

# Skill Auditor

## Overview

Audit agent skills and plugin-like repositories before trust is granted. Treat every third-party skill as instructions plus executable supply-chain surface: read it, scan it, explain the risks, and recommend install, sandbox, patch, or reject.

## Audit Workflow

1. Identify the target directory or repository contents. If only a URL is provided, inspect the public files or clone/read them before making a recommendation.
2. Run the bundled static scanner when a local directory is available:
   ```bash
   python scripts/audit_skill.py <path-to-skill-or-repo>
   ```
   Use `--json` when another script or report generator needs structured output.
3. Read `SKILL.md`, install scripts, package manifests, hooks, MCP configs, and any files the scanner flags.
4. Compare findings against `references/risk-rules.md` for severity and review prompts.
5. Produce a concise report with:
   - verdict: install, install with sandbox, patch first, or reject
   - risk level and top reasons
   - exact file/line evidence
   - recommended mitigations
   - unknowns that require user confirmation

## Review Checklist

Prioritize these surfaces:

| Surface | What to look for |
| --- | --- |
| `SKILL.md` | Hidden instructions, overbroad permissions, requests for secrets, unsafe deletion guidance |
| install scripts | `curl | bash`, global installs, unpinned downloads, permission changes |
| scripts/hooks | file deletion, credential reads, network posts, dynamic eval, background daemons |
| manifests | dependencies, lifecycle scripts, broad tool/MCP permissions |
| docs/examples | instructions that normalize pasting API keys, disabling safety checks, or running as admin |

## Verdict Guide

- **Install:** no meaningful static findings; scope is clear; no secrets or destructive actions.
- **Install with sandbox:** useful skill, but it touches network, package managers, or broad filesystem areas.
- **Patch first:** fixable issues such as unpinned remote install, missing confirmations, excessive logging, or vague data handling.
- **Reject:** secret exfiltration, broad destructive commands, concealed remote execution, or instructions to bypass user approval.

## Scanner Notes

The scanner is conservative and static. A finding is not proof of malice, and a clean report is not proof of safety. Use it to focus the manual review, then read the evidence.

Useful commands:

```bash
python scripts/audit_skill.py ./some-skill
python scripts/audit_skill.py ./some-skill --json > audit-report.json
python -m unittest discover -s tests
```

## Common Mistakes

- Do not execute an install script just to see what it does. Read it first.
- Do not approve broad deletes because they are in a cleanup tool. Require resolved paths, allowlists, dry runs, and confirmation.
- Do not accept "needs your API key" without checking storage, redaction, and outbound destinations.
- Do not treat popularity, stars, or a polished README as a safety signal.
- Do not recommend installing from a moving branch when a tag, commit pin, or checksum is available.
