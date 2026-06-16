# Delegated Engineering Roadmap for Manbaj ERP

## CEO Triage
The current company priority is to move the baklava factory ERP from MVP foundation to a controlled customer showcase and pilot. The work is primarily technical, so the CEO delegates execution to the Founding Engineer / CTO.

Parent issue: **NEZ-1 - Hire your first engineer and create a hiring plan**

## Delegation Summary

| Work packet | Owner | Priority | Disposition |
| --- | --- | --- | --- |
| Pilot readiness hardening | CTO | High | Ready to create child issue |
| Operational reconciliation workflows | CTO | High | Ready to create child issue |
| CSV import validation and reporting | CTO | Medium | Ready to create child issue |
| Cloud deployment readiness | CTO | High | Ready to create child issue |
| Showcase/UAT evidence package | CTO | Medium | Ready to create child issue |

## Child Issue Drafts

Use these drafts to create child issues with `parentId` set to NEZ-1 once Paperclip API access is restored.

### 1. Pilot readiness hardening

- **Assignee:** CTO
- **Objective:** Harden the MVP backend so it is safe enough for controlled showcase and pilot use.
- **Context:** The current MVP notes identify token-based auth, MVP bootstrap credentials, threshold approvals, basic CSV validation, and incomplete API response contracts as known limitations.
- **Acceptance criteria:**
  - Token expiry or rotation behavior is implemented or explicitly configured.
  - MVP default admin credentials are removed, disabled by default, or clearly gated behind local-only setup.
  - Environment configuration is documented for pilot deployments.
  - Error handling follows a consistent API response contract.
  - Existing MVP flow tests still pass, with focused tests added for new security/error behavior.
- **Next action:** CTO inspects `mvp_backend/app/auth.py`, `mvp_backend/app/main.py`, and current tests, then proposes the smallest hardening change set.

### 2. Operational reconciliation workflows

- **Assignee:** CTO
- **Objective:** Add the backend support needed for daily store reconciliation and auditable exception handling.
- **Context:** Current docs require end-of-day store reconciliation and approval controls. The MVP implementation already supports stock adjustments and transfer discrepancy handling.
- **Acceptance criteria:**
  - Daily reconciliation endpoint records store, date, expected stock, counted stock, variances, and closing status.
  - Reconciliation closure is auditable and cannot be silently overwritten.
  - Transfer discrepancy and stock adjustment workflows support rejection reasons.
  - Approval queue endpoints expose pending exceptions for manager action.
  - Tests cover happy path, variance path, and rejection path.
- **Next action:** CTO designs the model/service/API changes needed for reconciliation without disrupting existing inventory flows.

### 3. CSV import validation and reporting

- **Assignee:** CTO
- **Objective:** Make CSV imports usable for real MVP data preparation by returning actionable row-level validation results.
- **Context:** Current CSV import assumes clean templates. UAT and showcase data will need clear failure reports to avoid manual debugging.
- **Acceptance criteria:**
  - CSV import endpoints return row-level validation errors for failed records.
  - Import responses include created count, skipped count, failed count, and error details.
  - Invalid rows do not partially corrupt inventory or master data.
  - Documentation includes expected CSV templates and common error examples.
  - Tests cover valid imports, malformed rows, missing references, and duplicate handling.
- **Next action:** CTO reviews current import endpoints and schemas, then adds structured validation output.

### 4. Cloud deployment readiness

- **Assignee:** CTO
- **Objective:** Prepare a cloud-first deployment path for controlled showcase and pilot operations.
- **Context:** The ERP master plan recommends a cloud-first MVP with domain, SSL, hosting, monitoring, and backup/restore controls.
- **Acceptance criteria:**
  - Deployment runbook exists for the selected cloud target.
  - Environment variables and secrets are documented without exposing secret values.
  - Health check endpoint or documented health verification path exists.
  - Backup and restore smoke-test procedure is documented.
  - Minimal monitoring/logging baseline is documented.
- **Next action:** CTO selects the lowest-friction pilot deployment architecture and writes the implementation/runbook plan before changing infra.

### 5. Showcase/UAT evidence package

- **Assignee:** CTO
- **Objective:** Package the MVP so the CEO can confidently run a stakeholder showcase and UAT cycle.
- **Context:** Existing docs include MVP test scenarios, UAT scripts, demo-day script, and a 30-day execution calendar.
- **Acceptance criteria:**
  - Demo seed data or setup script supports repeatable showcase preparation.
  - API quick-start steps are verified against the current backend.
  - Known limitations are current and separated into pilot blockers vs acceptable MVP constraints.
  - Test evidence is recorded after changes.
  - UAT handoff notes identify what the CEO/customer should validate.
- **Next action:** CTO reconciles `docs/mvp/*` with the current backend behavior and closes gaps required for demo repeatability.

## CEO Follow-Up Cadence

The CEO should review CTO updates for:

- scope changes that affect customer commitments
- security or data-integrity risks
- blockers requiring board/user decisions
- readiness evidence before any customer-facing showcase

## Current Execution Note

This roadmap is ready for delegation. Live Paperclip child issue creation is blocked in this heartbeat because the runtime API refused connections. Once Paperclip API access is restored, create the five child issues above and assign them to the CTO.
