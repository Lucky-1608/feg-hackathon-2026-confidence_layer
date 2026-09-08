# Documentation

This directory contains the design record and implementation evidence for Confidence Layer. The repository [README](../README.md) is the starting point for setup and daily development.

## Architecture

- [Architecture overview](architecture/overview.md) describes the current layers and critical decision path.
- [ADR-001: Hexagonal architecture](decisions/0001-hexagonal-architecture.md) records the main design decision and its tradeoffs.

## Safety and security

- [Security implementation status](safety/security-controls.md) separates current demo controls from requirements for operator deployment.
- [Security reporting policy](../SECURITY.md) explains how to report a suspected vulnerability privately.

## Planning and evaluation

- [Implementation plan](evaluation/implementation-plan.md) is the original delivery plan and contains historical paths and assumptions.
- [Initial implementation audit](evaluation/implementation-audit.md) is a historical snapshot of the repository before implementation.
- [Implementation handoff, 2026-09-08](evaluation/implementation-handoff-2026-09-08.md) records the eight-phase implementation, current verification and remaining integration work.
- [Production audit, 2026-09-06](evaluation/production-audit-2026-09-06.md) is the earlier readiness assessment and hardening record.

Historical documents are retained for context. Where they conflict with the current source, automated tests, or production audit, the current implementation and newer evidence take precedence.

## Documentation rules

- Update public setup and command changes in the root README.
- Add durable architecture decisions under `decisions/`.
- Put current design descriptions under `architecture/`.
- Put safety and threat analysis under `safety/`.
- Put dated audits and evaluation plans under `evaluation/`.
- Link new maintained documents from this index.
