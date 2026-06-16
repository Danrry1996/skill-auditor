# Risk Rules

Use this reference when interpreting scanner output or manually reviewing files.

## Critical

- Remote code execution from the network: `curl ... | bash`, `wget ... | sh`, `irm ... | iex`. <!-- skill-auditor: ignore -->
- Broad destructive filesystem operations: `rm -rf ~`, root deletes, recursive deletes over computed paths without allowlists. <!-- skill-auditor: ignore -->
- Instructions to paste credentials into chat, logs, issues, or scripts that transmit them.
- Hidden persistence or background daemons without a clear stop/remove path.

Default verdict: reject or patch before any install.

## High

- Access to `.ssh`, private keys, API keys, token stores, browser profiles, or full environment dumps. <!-- skill-auditor: ignore -->
- Overbroad permissions such as `chmod 777`, writable shared directories, or admin-only setup without justification. <!-- skill-auditor: ignore -->
- Unreviewed lifecycle scripts in `package.json`, shell installers, or PowerShell bootstrap scripts.
- Network upload of local files or environment state.

Default verdict: patch first or install only in a throwaway sandbox.

## Medium

- Global package installs, unpinned dependencies, broad `pip install`/`npm install -g` guidance. <!-- skill-auditor: ignore -->
- Dynamic evaluation such as `eval`, `exec`, `Invoke-Expression`, or `new Function`.
- Writes outside the project or skill directory.
- Claims of cross-platform support without path handling or safety checks.

Default verdict: sandbox or request a safer install path.

## Low

- Documentation gaps, missing license, unclear update flow, missing tests, or weak examples.
- Benign network reads with clear destinations.
- Local read-only analysis.

Default verdict: install if the user accepts the limitations.

## Manual Review Prompts

Ask these questions before the final verdict:

1. What data can leave the machine?
2. What local paths can be read, written, moved, or deleted?
3. Can the skill execute downloaded code?
4. Are dependencies pinned or fetched from moving branches?
5. Does the user get a confirmation before irreversible actions?
6. Is there a clear uninstall or rollback path?
7. Does the skill work with least privilege?
