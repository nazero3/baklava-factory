# MVP Setup and Configuration Steps

## Objective
Configure a working MVP environment that can be demonstrated and tested end-to-end.

## Step-by-Step Execution Plan

## Step 1: Kickoff and Readiness (Day 1)
### Activities
- Confirm MVP scope and users
- Confirm cloud-first MVP environment
- Confirm single source of truth for master data files

### Owner
- Project Lead

### Output
- Signed MVP scope baseline
- Final role/user list

## Step 2: Environment Setup (Day 2-3)
### Activities
- Create MVP environment (application + database)
- Configure organization profile and locations (factory + 3 stores)
- Configure security baseline (password policy and role templates)

### Owner
- System Admin

### Output
- Accessible MVP environment
- User login readiness

## Step 3: Master Data Configuration (Day 4-6)
### Activities
- Import products, raw materials, suppliers, and stores
- Load recipe/BOM with yield assumptions
- Validate units of measure (kg/gram conversions)

### Owner
- Operations Lead + Accounting Lead

### Output
- Approved master data version

## Step 4: Opening Stock and Cost Baseline (Day 7-8)
### Activities
- Import opening stock by location and lot
- Validate starting valuation with accounting
- Reconcile stock totals with warehouse baseline

### Owner
- Warehouse Lead + Accountant

### Output
- Reconciled opening balances

## Step 5: Workflow Configuration (Day 9-10)
### Activities
- Configure transaction flows:
  - Purchasing and receiving
  - Material issue to production
  - Production posting
  - Transfer dispatch and receipt
  - Store daily movement and reconciliation
- Configure approval thresholds for stock adjustments

### Owner
- Project Lead + System Admin

### Output
- Ready-to-test operational flows

## Step 6: Reporting and Dashboard Setup (Day 11)
### Activities
- Enable daily KPI dashboard
- Validate key reports:
  - Stock position
  - Waste
  - Transfer status
  - Cost and margin

### Owner
- Accountant + Executive User

### Output
- Approved report list for MVP

## Step 7: Internal Dry Run (Day 12-14)
### Activities
- Run end-to-end process with sample transactions
- Capture defects and process gaps
- Apply corrections and re-test

### Owner
- Core project team

### Output
- Dry-run completion report
- UAT readiness decision

## Step 8: UAT Preparation (Day 15)
### Activities
- Prepare UAT scripts and expected results
- Assign business users to each scenario
- Freeze major config changes during UAT

### Owner
- Project Lead

### Output
- UAT schedule and participant list

## Step 9: UAT Execution (Day 16-20)
### Activities
- Execute all business-critical scenarios
- Record pass/fail, defects, and retest results
- Track final acceptance criteria

### Owner
- Business users + QA coordinator

### Output
- Signed UAT report

## Step 10: Showcase Day and Decision (Day 21-22)
### Activities
- Live demonstration to customer stakeholders
- Present KPI improvements and process evidence
- Collect go/no-go decision for expanded rollout

### Owner
- Business Sponsor + Project Lead

### Output
- Showcase sign-off
- Next-phase roadmap decision

## Documentation Control
- Every step must produce a dated artifact
- Store all evidence in a shared `docs/mvp` folder
- Use version naming format: `vX.Y_YYYY-MM-DD`
