# Baklava Factory ERP Master Plan

## 1) Business Goal
Build one simple system that tracks everything going in and out:
- Raw materials purchased and received (flour, ghee, nuts, sugar, packaging)
- Production conversion from ingredients to finished baklava by recipe/batch
- Transfers from factory to 3 stores by kilograms
- Sales, returns, and waste by store
- Real-time stock visibility at factory and stores
- Cost and profitability by product and store

## 2) Solution Options
### Option A: Cloud (Online)
- Central web-based system hosted online
- Easier scaling, remote access, lower internal IT burden
- Requires stable internet and backup connectivity

### Option B: On-Premise (Offline/Company-Only)
- System hosted on company infrastructure
- Full local data control and internal continuity
- Requires server hardware, IT support, and stricter local operations

## 3) Customer-Friendly SRS Scope
### Core Modules
1. Master data (products, recipes/BOM, suppliers, stores, users, permissions)
2. Purchasing and inbound receiving
3. Raw material inventory with lot tracking
4. Production orders with recipe-based consumption and yield/waste
5. Distribution transfer notes by kilograms
6. Store stock operations (receive, sale movement, returns, waste)
7. Inventory control (counting, variances, approvals)
8. Costing and profitability reporting
9. Dashboards and operational reports
10. Audit logs and data import/export

### Non-Functional Requirements
- Arabic-friendly and easy-to-use workflows
- Fast response time for daily operations
- Role-based security and approval controls
- Backup and restore controls
- Availability target (cloud) and uptime controls (on-prem)

### Acceptance Targets
- Stock accuracy >= 97% after stabilization
- 100% transfer records digitized
- Daily cost/kg and margin reporting available
- End-of-day store reconciliation enabled

## 4) Requirements for Each Option to Be Valid
### Cloud Validity Requirements
- Reliable internet at all sites + 4G failover
- Domain and SSL
- Hosting account and monitoring
- Security baseline (password policy, permissions, MFA for managers)
- Backup and restore testing

### On-Premise Validity Requirements
- Dedicated server + UPS + backup storage
- Firewall and endpoint protection
- VPN between factory and stores (if remote)
- IT administrator or managed IT partner
- Disaster recovery runbook and periodic restore drills

## 5) Data-Driven Execution Plan
### Phase 0: Discovery & Baseline (1-2 weeks)
- Map current process and collect baseline KPIs
- Confirm approval matrix and target workflows

### Phase 1: Solution Design (2 weeks)
- Finalize SRS, reports, and deployment choice

### Phase 2: Build & Configure (4-6 weeks)
- Configure modules, permissions, forms, templates

### Phase 3: Data Preparation & Migration (2-3 weeks, overlaps)
- Clean and import master data and opening stock
- Validate yields, costs, and stock balances

### Phase 4: Testing & Pilot (2 weeks)
- End-to-end pilot with factory + one store
- Resolve issues and confirm readiness

### Phase 5: Go-Live & Hypercare (2-4 weeks)
- Rollout to all stores
- Daily support, KPI monitoring, and handover

## 6) Estimated Timeline
- Cloud implementation: 12-16 weeks
- On-prem implementation: 14-20 weeks
- If both are prepared in parallel: 16-22 weeks

## 7) MVP Start Recommendation
Start with MVP first, then expand:
- Suggested MVP users: 12-15 users (standard)
- Suggested model: cloud-first
- MVP duration: 8-12 weeks
- MVP scope: inventory + production + transfer + store movement + dashboard

## 8) Commercial Estimate (Syrian Market Positioning)
Contract in USD with invoice-day SYP conversion.

### Cloud
- Implementation: USD 24,000-34,000
- Hosting/support: USD 450-1,100 monthly
- Training add-on: USD 1,500-3,000

### On-Premise
- Implementation: USD 28,000-42,000
- Hardware/network: USD 6,000-15,000
- Annual maintenance: 15%-22% of implementation

### Suggested Customer-Friendly Payment Milestones
- 20% kickoff
- 25% design sign-off
- 30% UAT pass
- 15% go-live
- 10% after hypercare completion

## 9) Recommendation to Maximize Customer Acceptance
- Lead with Cloud Base Package for faster and lower-friction adoption
- Keep On-Premise as a premium control-focused option
- Commit to measurable KPI improvement in first 6 weeks after go-live

## 10) Immediate Next Steps
- Assign business owner, operations lead, accounting lead
- Provide products, recipes, suppliers, stock, store list
- Confirm deployment choice and budget model
- Start discovery workshop and baseline measurement

---

## Related Detailed Documents
- `docs/00_executive_proposal_for_customer.md`
- `docs/01_scope_and_kpi_signoff_pack.md`
- `docs/02_cloud_vs_onprem_decision_guide.md`
- `docs/03_customer_friendly_srs.md`
- `docs/04_data_preparation_and_migration_playbook.md`
- `docs/05_rollout_uat_and_hypercare_execution_plan.md`
- `docs/06_commercial_and_pricing_proposal.md`
