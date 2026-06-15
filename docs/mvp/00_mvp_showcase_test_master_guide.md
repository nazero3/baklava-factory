# MVP Showcase and Test Master Guide

## Purpose
This guide defines how to run a real MVP trial for the baklava factory ERP before full rollout.  
It is designed for business users and project stakeholders to validate the solution quickly and safely.

## MVP Goal
Demonstrate and test the minimum end-to-end business flow:
1. Receive raw materials
2. Produce baklava from recipe
3. Transfer finished goods to 3 stores by kg
4. Record store movement (sales, returns, waste)
5. Review daily dashboard (stock, waste, cost, margin)

## MVP Duration
- Total: 4 weeks for showcase and controlled testing
- Week 1: Setup and data load
- Week 2: Internal dry run
- Week 3: User acceptance testing (UAT)
- Week 4: Live showcase with business stakeholders

## MVP Team Structure
- Business Sponsor (owner/GM): final approval
- Project Lead: day-to-day coordination
- Operations Lead: process owner (factory)
- Accounting Lead: costing and reconciliation owner
- Store Champion: one representative for all stores
- System Admin: user access and environment control

## What Is Included in MVP
- Inventory (raw + finished)
- Production orders and consumption by recipe
- Transfer to stores
- Store stock movement
- KPI dashboard and operational reports
- Audit logs and role permissions

## What Is Not Included in MVP
- Advanced forecasting and BI
- Full POS deep integration (manual or CSV summary in MVP)
- Multi-factory support
- Native mobile app

## MVP Success Criteria
1. All mandatory business flows executed successfully at least 3 times
2. 100% of transfer transactions captured digitally
3. Daily stock and margin report generated without manual spreadsheet merge
4. Stock variance in test cycles remains within approved threshold
5. Stakeholders sign off that MVP is ready for phased production rollout

## Risk Controls During MVP
- Use test environment first, then limited production trial
- Freeze master data changes during UAT week
- Keep rollback method ready for every test cycle
- Record all defects and assign owners with due dates

## Deliverables Produced by MVP
- Scope sign-off and role matrix confirmation
- Tested configuration baseline
- Clean data templates and validated import files
- UAT evidence with pass/fail records
- Showcase script and stakeholder feedback log
- Go/no-go recommendation for full rollout

## Document Map
- `docs/mvp/01_mvp_scope_users_and_roles.md`
- `docs/mvp/02_mvp_setup_and_configuration_steps.md`
- `docs/mvp/03_mvp_test_scenarios_and_uat_scripts.md`
- `docs/mvp/04_mvp_demo_day_script.md`
- `docs/mvp/05_mvp_tracking_templates.md`
