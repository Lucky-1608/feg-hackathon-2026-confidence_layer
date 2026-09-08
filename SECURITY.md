# Security policy

Confidence Layer is a synthetic local prototype and is not approved for production or real customer data.

## Reporting a vulnerability

Do not report a suspected vulnerability in a public issue.

Use the repository's private GitHub security-advisory process when it is available. If private advisories are unavailable, contact a repository maintainer through the organization's private communication channel and include:

- The affected component and revision.
- Reproduction steps or a minimal proof of concept.
- The observed and expected behavior.
- The likely impact and any known workaround.

Do not include real customer, identity, betting, credential, or operator data in a report.

## Response expectations

Maintainers should acknowledge a report, establish a private owner, assess severity, and coordinate remediation before public disclosure. Response times are not currently guaranteed because this is a hackathon prototype.

## Supported versions

Only the current `main` branch is maintained. No released production versions exist.

## Current limitations

The local demo uses a fixed `demo-token`, synthetic providers, local service credentials, and permissive CORS. These are development-only boundaries. Review the [security implementation status](docs/safety/security-controls.md) and [production audit](docs/evaluation/production-audit-2026-09-06.md) for the complete set of known gaps.
