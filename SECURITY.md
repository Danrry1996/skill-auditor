# Security Policy

## Reporting a Vulnerability

Please report security issues privately instead of opening a public issue with exploit details.

Open a GitHub security advisory for this repository, or contact the maintainer through the GitHub profile linked from the repository owner.

Please include:

- affected file or rule
- reproduction steps
- expected risk impact
- whether the issue causes false negatives, false positives, or unsafe guidance

## Scope

In scope:

- scanner false negatives for dangerous skill patterns
- unsafe guidance in `SKILL.md` or references
- command examples that could encourage unsafe installation
- vulnerabilities in bundled scripts

Out of scope:

- risks in third-party skills being audited
- social engineering against maintainers
- denial-of-service reports that only affect local manual scans

## Project Safety Model

`skill-auditor` performs static review and does not execute the target repository. A clean report does not prove a skill is safe; it only means the bundled static rules did not detect known patterns.
