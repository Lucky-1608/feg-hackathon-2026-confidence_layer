# Security implementation status

The default configuration is a local demo. JWT authentication and operational controls are implemented; operator integration and deployment validation remain required. See the [implementation handoff](../evaluation/implementation-handoff-2026-09-08.md) for current evidence and limitations.

## Current controls

- Decision, event, outcome, SQS and Prometheus endpoints require bearer authentication and scopes. JWT mode validates RS256 signatures through HTTPS JWKS, issuer, audience, expiry, subject and operator claims. Redis binds sessions to identities; idempotency keys include the identity. The fixed `demo-token` remains available only for the local demo.
- Demo authentication and synthetic safety/slip/market providers are restricted to `APP_ENV=development/local/test`, `DEMO_MODE=true`, and `AUTH_PROVIDER=development`. JWT mode requires issuer, audience and JWKS configuration. Its operator authority adapters remain unavailable placeholders that suppress intervention. These defaults are for local development only.
- Safety constraints precede policy selection, and a policy result must belong to the eligible set. Unknown/blocked safety, insufficient state confidence and legitimate reconsideration produce `NO_INTERVENTION`.
- Provider facts are separate from request telemetry. The current providers return synthetic facts; they are not connected to an operator.
- API response text uses static templates, and the demo renders it with `textContent`.
- Redis rate limits enforce actor, IP and global quotas. The global kill switch requires `admin:global`; lookup failures suppress intervention. Shadow mode audits the proposed decision while returning no intervention.
- Outcome and reward publications use a transactional outbox. Decision audits remain asynchronous, with bounded shutdown draining and error metrics; abrupt termination can still lose pending audit writes.

## Required before operator deployment

- Validate the JWT/JWKS integration against the selected identity provider and enforce authoritative slip ownership in real operator adapters. Exercise tenant isolation and key rotation with production-equivalent infrastructure.
- Define complete authoritative safety/fact contracts and reject unknown, stale, invalid or mismatched inputs. Add real operator adapters behind the existing interfaces.
- Define retention, deletion and redaction. Opaque actor identifiers alone do not enforce absence of PII: event dictionaries and DLQ messages can contain arbitrary data, and exception logs can include input values.
- Enforce TLS/credentials for services, manage production secrets, restrict origins/network access, configure request/body limits and validate the implemented Redis rate limits, and validate dependency/image security. Local Compose credentials and open ports are development settings.
- Provide durable, reconcilable audit delivery and tested event recovery; validate authorization, spoofing, duplicate/replay, outage and overload cases in integration tests.

Health, readiness, documentation and UI routes are not bearer-protected. Wildcard CORS remains enabled for the demo. This document does not claim those endpoints or the deployment are production-hardened, and it is not a legal or regulatory certification.
