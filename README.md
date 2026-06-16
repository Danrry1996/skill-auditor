# Skill Auditor

![Skill Auditor hero](assets/skill-auditor-hero.png)

Audit third-party agent skills, Claude Code plugins, Codex skills, and install scripts before you trust them.

`skill-auditor` gives an agent a repeatable review workflow plus a static scanner for common risk signals: remote shell pipes, broad deletes, credential access, unsafe permissions, dynamic eval, network posts, and global installs.

## Quick Start

Install as an agent skill by cloning this repository into your skills folder:

```bash
git clone https://github.com/<your-username>/skill-auditor.git ~/.codex/skills/skill-auditor
```

Then ask:

```text
Use skill-auditor to review this skill before I install it: <path-or-url>
```

Run the scanner directly:

```bash
python scripts/audit_skill.py ./some-skill
python scripts/audit_skill.py ./some-skill --json > audit-report.json
```

## What It Checks

- `SKILL.md` instructions that ask for secrets, broad permissions, or unsafe cleanup
- install scripts that pipe remote downloads into shells
- scripts/hooks that read credentials, delete broad paths, post data, or run dynamic eval
- package/manifests with global installs or lifecycle risk
- missing confirmation, rollback, sandbox, and data-handling boundaries

## Output

The skill produces a human verdict:

- `install`
- `install with sandbox`
- `patch first`
- `reject`

The bundled script can also emit JSON for automation.

## Limits

This is static analysis plus human review guidance. It can find obvious risk patterns, but it cannot prove a third-party skill is safe.
