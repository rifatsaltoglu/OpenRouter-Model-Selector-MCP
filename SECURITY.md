# Security Policy & Vulnerability Disclosure

## Named Security Maintainer

This open-source Model Context Protocol (MCP) project is maintained and audited for security by:

- **Full Name:** Rifat Saltoğlu (Rifat Saltoglu)
- **Role:** Lead Security Maintainer & Principal Author
- **GitHub Handle:** [@rifatsaltoglu](https://github.com/rifatsaltoglu)
- **Security Contact:** `rifatsaltoglu@gmail.com`
- **Repository:** [https://github.com/rifatsaltoglu/OpenRouter-Model-Selector-MCP](https://github.com/rifatsaltoglu/OpenRouter-Model-Selector-MCP)

---

## Supported Versions

| Version | Supported          | Security Auditing Status |
| ------- | ------------------ | ------------------------ |
| 1.0.x   | :white_check_mark: | Active SAST & Dependency Monitoring |

---

## Scope of Defensive Security Work

As a Model Context Protocol (MCP) server consumed by LLM agents (Claude Desktop, Cursor, and MCP-compatible IDE runtimes), security verification focuses on:

1. **Indirect Prompt Injection Prevention:** Sanitizing upstream metadata and model descriptions fetched from external APIs (`/api/v1/models`) before injecting context into the host LLM.
2. **Transport & SSRF Hardening:** Strict URL validation and TLS verification on outbound requests (`httpx` / `urllib`) to prevent Server-Side Request Forgery.
3. **Supply-Chain & Dependency Auditing:** Continuous auditing of `fastmcp`, `pydantic`, and transitive Python dependencies against known CVEs.

---

## Reporting a Vulnerability (Coordinated Disclosure)

If you discover a security vulnerability within `OpenRouter-Model-Selector-MCP`, please report it privately via coordinated disclosure:

1. **Email:** Send details to **Rifat Saltoğlu** at `rifatsaltoglu@gmail.com` with the subject `[SECURITY] OpenRouter-Model-Selector-MCP`.
2. **GitHub Security Advisories:** Alternatively, submit a draft advisory via [GitHub Security Advisories](https://github.com/rifatsaltoglu/OpenRouter-Model-Selector-MCP/security/advisories).
3. **Response SLA:** Initial triage within 24 hours; patch release and public advisory credit within 7 days.

---

## Security Advisories & Audit Log

### Advisory OR-MCP-2026-001: Context Sanitization Against Indirect Prompt Injection in Upstream Model Metadata
- **Discoverer & Maintainer:** Rifat Saltoğlu (`@rifatsaltoglu`)
- **Severity:** Medium (CVSS 6.5)
- **Component:** `openrouter_agent_selector.py` (`select_best_agent` response formatter)
- **Summary:** Upstream model metadata strings returned by third-party catalog endpoints could contain untrusted control tokens or instruction-override payloads when rendered directly into an MCP tool response.
- **Mitigation:** Enforced strict field whitelisting (`id`, `name`, numeric `pricing`, validated modality tags) and stripped raw unvalidated description payloads from tool output.
