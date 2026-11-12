# h4-reposentinel — commercial scaling roadmap

**Creator & technical direction: Chris Cruz — @h4ckd4d.**

## Current increment
CI policy gate for configurable finding budgets (exit code 2 on failure). `reposentinel scan . --max-findings 0`

## Production blockers
1. Enterprise SSO, tenant isolation, RBAC and full audit controls.
2. PostgreSQL migrations, async jobs, queues, retries and idempotency.
3. Rate limits, quotas, metered plans and billing.
4. Observability, incident response, backup/restore drills, security reviews.
5. Load testing, accessibility, localization and production SLAs.
6. Customer discovery, pilot outcomes, commercial/legal documentation.

The current prototype does not support production customer workloads. MIT source does not equal a managed SaaS or a verified security guarantee.
