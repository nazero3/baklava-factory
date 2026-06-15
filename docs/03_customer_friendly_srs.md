# Software Requirements Specification (SRS)
## Baklava Factory End-to-End Management System

## 1. Document Purpose
This SRS defines what the solution must do to manage inbound materials, production, and outbound distribution by kilograms for one factory and three stores.

## 2. Business Objectives
- Control all inbound and outbound movements
- Improve stock accuracy and reduce losses
- Make production and transfer decisions based on daily data
- Provide transparent product cost and margin by store

## 3. Scope
The solution covers:
- Purchasing and receiving
- Raw material inventory
- Production management with recipe conversion
- Finished goods inventory
- Transfers to stores
- Store-level stock and sales movement
- Reporting and KPI dashboard
- Audit trail and role-based security

## 4. Users and Permissions
- Owner/Executive: dashboard and approvals
- Factory Manager: operations oversight, approvals
- Warehouse User: receiving, stock movement, counting
- Production Supervisor: production order execution
- Store Manager/Cashier: receipt, sale movement, returns, waste
- Accountant: cost review, reconciliation, margin reporting
- System Administrator: user and configuration management

## 5. Functional Requirements
### FR-01 Master Data
- Product catalog with categories and units
- Recipe (BOM) management with ingredient quantities per kg output
- Supplier master and store master
- User roles and permission groups

### FR-02 Purchasing and Receiving
- Create purchase orders and receive materials
- Record batch/lot, quantity, and supplier cost
- Update stock automatically upon goods receipt

### FR-03 Raw Material Inventory
- Stock ledger with in/out transactions
- Lot-based traceability
- Minimum stock and reorder alerts

### FR-04 Production Planning and Execution
- Create production orders by product and target kg
- Auto-consume ingredients based on active recipe version
- Record actual output, losses, and adjustments
- Post finished goods to inventory

### FR-05 Distribution to Stores
- Create transfer by product and kilograms
- Track transfer states: drafted, dispatched, in-transit, received
- Confirm receipt per store and handle differences

### FR-06 Store Operations
- Receive transfer stock
- Register sales movement (from POS import or manual summary)
- Record returns and spoilage/waste
- End-of-day stock reconciliation

### FR-07 Stock Counting and Adjustment
- Support cycle counts and full physical counts
- Record variance and require approval above threshold

### FR-08 Cost and Margin
- Weighted average cost per kg
- Gross margin report by product and store
- Daily cost visibility

### FR-09 Reporting and Dashboard
- Daily production summary
- Raw and finished stock position
- Transfer status report
- Sales vs production trend
- Waste dashboard
- Top products by volume and margin

### FR-10 Audit and Compliance
- Transaction history for all critical actions
- Who changed what and when
- Exportable audit logs

### FR-11 Data Import/Export
- Excel/CSV templates for master data
- Scheduled exports for accounting and management

## 6. Non-Functional Requirements
### NFR-01 Usability
- Arabic-friendly labels and forms
- Simple workflows for non-technical users
- Mobile-friendly browser screens

### NFR-02 Performance
- Most screens load in less than 2 seconds under normal load
- Daily reports available within acceptable operational time window

### NFR-03 Availability
- Cloud option target: 99.5% monthly availability
- On-premise target: high local uptime with backup and recovery controls

### NFR-04 Security
- Role-based access control
- Password policy and optional MFA for managers
- Backup and restore procedures

### NFR-05 Reliability and Recovery
- Daily backup
- Monthly restore test (cloud) / quarterly full DR drill (on-premise)

## 7. Deployment-Specific Requirements
### 7.1 Cloud
- Internet at each site and 4G backup
- Hosted environment, SSL, and monitoring
- Managed update cycle

### 7.2 On-Premise
- Server, UPS, firewall, VPN
- Internal/outsourced IT maintenance
- Patch and backup verification process

## 8. Interfaces and Integrations
- Optional POS import for daily sales movement
- Optional accounting export
- CSV import/export baseline is mandatory

## 9. Data Requirements
- Product master with units and conversion rules
- Recipe master with yield assumptions
- Supplier and store masters
- Opening stock by lot/location
- Historical transaction import (optional 3-6 months)

## 10. Acceptance Criteria (UAT Exit)
1. Stock accuracy reaches at least 97% during stabilization window
2. 100% of factory-to-store transfers are digitally recorded
3. Daily cost per kg and margin reports are available
4. End-of-day reconciliation process is completed by all stores
5. Report preparation effort is reduced versus baseline

## 11. Assumptions
- Stakeholders provide complete and clean source data
- Roles and approval matrix are finalized before UAT
- One process owner is assigned at factory and each store

## 12. Constraints
- Release 1 focuses on core operational control
- Advanced analytics and additional integrations are optional add-ons

## 13. SRS Approval Sheet
- Business Owner: __________ Date: __________
- Operations Lead: __________ Date: __________
- Accounting Lead: __________ Date: __________
- Project Manager: __________ Date: __________
