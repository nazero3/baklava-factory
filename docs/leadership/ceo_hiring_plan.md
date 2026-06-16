# CEO Hiring Plan: Founding Engineer / CTO

## Context
Issue NEZ-1 asks the CEO to hire the first engineer, create a hiring plan, break the ERP roadmap into concrete tasks, and start delegation for the Manbaj project.

The company already has an MVP backend foundation for the baklava factory ERP with inventory, production, transfers, store movements, authentication, approvals, CSV import/export, and automated MVP-flow tests. The next operating priority is to convert this into an accountable engineering delivery stream.

## Hiring Decision
Hire the first engineering direct report as:

- **Role:** Founding Engineer / CTO
- **Reports to:** CEO
- **Primary ownership:** Technical strategy, delivery execution, architecture, code quality, infrastructure, developer workflow, and engineering delegation
- **Initial mission:** Turn the existing ERP MVP foundation into a reliable customer-showcase and controlled-pilot product for Manbaj

This role is the correct first hire because the immediate roadmap is primarily technical: production hardening, API quality, security controls, reconciliation workflows, deployment readiness, and technical task decomposition.

## Role Scorecard

### Outcomes owned in the first delivery cycle
1. Convert the MVP backend into a pilot-ready ERP service.
2. Maintain a clear technical roadmap with small, testable work items.
3. Establish a minimum engineering baseline for security, testing, deployment, observability, and release notes.
4. Keep the CEO informed through concise status updates, blockers, and decisions needed.

### Required strengths
- FastAPI/Python backend delivery
- Data modeling for inventory, production, and accounting-adjacent workflows
- Security-minded API design
- Test strategy and CI discipline
- Pragmatic cloud deployment judgment
- Ability to break ambiguous business workflows into engineering tasks

### Near-term technical baseline
- Each technical task has a named owner, objective, acceptance criteria, and verification command.
- No production-facing default credentials remain in release artifacts.
- Critical stock, transfer, production, and reconciliation paths remain covered by automated tests.
- Delivery notes distinguish MVP limitations from pilot blockers.

## Delegation Model

The CEO delegates technical implementation to the CTO. The CTO may create additional subtasks for backend, infrastructure, QA, or design support as needed.

The CEO remains responsible for:
- product priority
- customer-facing tradeoffs
- approval of scope changes
- resolving cross-functional ambiguity
- escalating blockers to the board/user

The CTO is responsible for:
- implementation plans
- code changes
- technical reviews
- test and deployment evidence
- identifying when UX, CMO, or board input is required

## Immediate Delegated Engineering Priorities

1. **Pilot readiness hardening**
   - Secure token/session behavior
   - Remove or gate MVP-only bootstrap credentials
   - Define environment configuration
   - Add response contract and error handling baseline

2. **Operational reconciliation**
   - Daily store closure
   - Signed reconciliation log
   - Transfer discrepancy rejection reasons
   - Approval queue endpoints

3. **Data import reliability**
   - CSV validation reports
   - Row-level errors
   - Import summary output
   - Safer master-data loading for showcase/UAT

4. **Deployment readiness**
   - Cloud-first deployment runbook
   - Backup/restore smoke test
   - Health check and monitoring baseline
   - Minimal release checklist

5. **Showcase readiness**
   - Demo seed data
   - API quick-start verification
   - Known limitations list
   - UAT evidence package

## Acceptance Criteria for NEZ-1

NEZ-1 is complete when:

- A founding engineer/CTO role is defined as the first engineering hire.
- The hiring plan names the role, mission, reporting line, scorecard, and immediate priorities.
- The Manbaj ERP roadmap is broken into concrete delegated technical work packets.
- Each delegated packet has owner, objective, acceptance criteria, and next action.
- The CEO leaves a durable task update explaining delegation and blockers.

## Current Blocker

During this heartbeat, the Paperclip API endpoint provided by the runtime refused connections from the cloud shell. Because of that, the CEO could not create live Paperclip child issues or comments through the API in this run.

Named unblock owner/action:

- **Owner:** Paperclip platform/runtime
- **Action:** Restore API reachability for `PAPERCLIP_API_URL`, then create the child issues from `docs/leadership/delegated_engineering_roadmap.md` with `parentId` set to NEZ-1 and assignee set to the CTO.

Until the API is reachable, this document and the delegated roadmap are the durable fallback work products.
