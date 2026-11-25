# Security Policy

## Local-Only & Air-Gap Design
Jarvis OS adheres strictly to the **Wi-Fi-Off Law**:
- The core daemon binds exclusively to loopback (`127.0.0.1:4700`).
- Local LLM inference binds to `127.0.0.1:11434`.
- Sensitive configuration files (`config.json`) are blocked from HTTP static serving (`403 Forbidden`).
- Interactive shell endpoints evaluate commands through `ShellAssistant.evaluate_safety()` to block destructive patterns (`rm -rf`, `mkfs`, raw block device writes, fork bombs).

## Reporting a Vulnerability
Please report suspected security issues via GitHub Security Advisories at `https://github.com/10JERRY01/Jarvis-os/security/advisories/new` rather than posting exploitable details in public issues.
