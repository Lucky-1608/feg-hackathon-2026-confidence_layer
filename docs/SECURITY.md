# Security Architecture

## Authentication
- All API endpoints are protected by OAuth2 Bearer tokens.
- Tokens must be signed by the trusted Identity Provider.

## Data Protection
- PII is not logged.
- The `anonymous_actor_id` is used instead of user IDs in core domains.
- Redis and PostgreSQL connections require TLS in production.
