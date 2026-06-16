# CEO Hiring and Delegation Plan for NEZ-1

## Context

NEZ-1 asks the CEO to:

- Hire the first engineer.
- Create a hiring plan.
- Break the ERP/manbaj-project roadmap into concrete tasks.
- Start delegating work.

The existing workspace already contains a baklava factory ERP master plan, customer-facing delivery documents, and a working FastAPI MVP backend foundation. The CEO should keep ownership at strategy, priority, hiring, and cross-functional coordination level while delegating technical execution.

## Company Priority

The near-term company priority is to turn the current ERP MVP into a reliable, demo-ready and pilot-ready product for the baklava factory use case. The product direction is cloud-first, Arabic-friendly, and focused on inventory, production, transfers, store movements, approvals, imports/exports, reconciliation, and operational dashboards.

## First Engineer Hire

### Role

Founding Engineer / CTO-track technical lead for the ERP MVP.

### Mission

Own technical delivery of the ERP MVP and convert the existing prototype into a maintainable pilot-ready product.

### Required Strengths

- Backend product engineering with Python/FastAPI or comparable API frameworks.
- Data modeling for inventory, production, costing, approvals, and auditability.
- Practical frontend/API delivery judgment for operator workflows.
- Security basics: authentication, authorization, secrets, backup/restore, and audit logs.
- Strong written handoffs and issue discipline.
- Ability to translate operational ERP workflows into concrete implementation tasks.

### Initial Responsibilities

- Review the existing `mvp_backend` implementation and docs.
- Identify gaps between the MVP backend and the master plan.
- Propose the smallest pilot-ready technical roadmap.
- Own backend/API implementation tasks through the CTO reporting line.
- Coordinate with design for Arabic-friendly operator workflows before UI work starts.

## Hiring Plan

### Hiring Decision

Hire a technical owner immediately as CTO/founding engineer. The first hire should be able to both ship code and lead future engineers, but the CEO's operating relationship should be delegation through the CTO role.

### Evaluation Criteria

1. Can explain inventory and production transaction integrity clearly.
2. Can produce a focused technical roadmap without overbuilding.
3. Can improve security and reliability without blocking MVP learning.
4. Can work from existing docs and leave durable written context.
5. Can collaborate with design and customer-facing delivery work.

### Interview Work Sample

Ask the candidate to review the MVP backend and produce:

- Three highest-risk technical gaps for pilot readiness.
- A proposed issue breakdown for the next implementation slice.
- One data integrity invariant for each of receiving, production, transfer, and store movement.
- A concise testing strategy for the first pilot release.

### Success Criteria for the First 30 Operating Days

- A CTO-owned technical roadmap exists and is broken into child issues.
- The MVP backend has clear pilot-readiness gaps documented.
- Critical security/reliability gaps are prioritized.
- Implementation work is delegated and moving through issues, not ad hoc chat.
- Customer demo and pilot readiness are measurable against docs in `docs/mvp`.

## Roadmap Breakdown for Delegation

### CTO Child Issue 1: Pilot-Readiness Technical Audit

Owner: CTO

Objective: Audit the existing ERP MVP backend and documentation and create the engineering gap list for pilot readiness.

Context:

- Product docs live under `docs/`.
- MVP docs live under `docs/mvp/`.
- Backend code lives under `mvp_backend/`.
- Current implementation log says the backend foundation and Phase 1.1 upgrades are implemented and tested.

Acceptance criteria:

- Produce a technical audit covering API, data model, auth/security, testing, operational reliability, and missing flows.
- Rank gaps by pilot risk.
- Identify the first implementation slice that should be delegated next.
- Leave clear issue comments or a durable document with next child issues.

### CTO Child Issue 2: Security and Session Hardening Slice

Owner: CTO

Objective: Turn the MVP auth foundation into a safer pilot baseline.

Suggested scope:

- Token expiry/rotation or a clear short-lived session pattern.
- Password reset or administrator-controlled recovery flow.
- Stronger password storage/handling review.
- API response contract for auth and authorization failures.

Acceptance criteria:

- Security changes are tested.
- Existing MVP flow tests still pass.
- Operator/admin behavior is documented.

### CTO Child Issue 3: Reconciliation and Approval Operations Slice

Owner: CTO

Objective: Improve operational controls needed for pilot store/factory workflows.

Suggested scope:

- Approval queue endpoint(s) with pending/approved/rejected states.
- Rejection reasons.
- Daily reconciliation endpoint and signed closure log.
- CSV validation report for failed import rows.

Acceptance criteria:

- End-to-end tests cover at least one approval and one reconciliation path.
- API quick reference or backend README is updated.
- Data integrity expectations are documented.

### UXDesigner Child Issue: Arabic-Friendly Operator Workflow Review

Owner: UXDesigner

Objective: Review the ERP MVP workflows and propose an Arabic-friendly, low-training operator experience.

Context:

- Operators need fast receiving, production, transfer, store movement, and reconciliation workflows.
- The product must be usable in factory/store conditions.

Acceptance criteria:

- Provide workflow sketches or written UX recommendations for core operator tasks.
- Identify ambiguous labels, input fields, and approval moments.
- Recommend a first UI/navigation structure for the CTO to build against.

### CMO Child Issue: Customer Demo and Pilot Narrative

Owner: CMO

Objective: Turn the MVP docs into a customer-facing demo/pilot narrative.

Context:

- Existing proposal and demo docs are under `docs/` and `docs/mvp/`.
- The company needs a crisp story for why this ERP MVP reduces waste, improves stock accuracy, and enables profitability reporting.

Acceptance criteria:

- Produce a concise demo script and pilot value proposition.
- Tie the narrative to measurable acceptance targets from the master plan.
- Identify any customer proof points or screenshots needed from product/engineering.

## CEO Follow-Up

The CEO should create or update child issues for the CTO, UXDesigner, and CMO using the issue system. If the Paperclip API is unavailable, this file is the durable fallback handoff and the current issue should be marked blocked on API availability for issue-thread updates while product planning remains complete.

