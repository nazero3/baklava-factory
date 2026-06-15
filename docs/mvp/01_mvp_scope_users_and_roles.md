# MVP Scope, Users, and Roles

## Recommended MVP User Option
For initial showcase and testing, use **Standard MVP (12-15 users)**.

## User Distribution (Example: 13 Users)
1. Business Owner / Executive: 1 (dashboard + approval)
2. Factory Manager: 1
3. Warehouse Users: 2
4. Production Supervisor: 1
5. Production Operators: 2
6. Store Manager/Cashier Users: 3 (one per store)
7. Accountant: 1
8. System Admin: 1
9. Project Support User: 1 (temporary during MVP only)

## Access Model Options
### Option A: Named Users (Best Practice)
- One login per person
- Highest accountability and best audit quality

### Option B: Shared Station Users
- One login per shift/location
- Lower accountability, only recommended for temporary MVP speed

### Option C: Hybrid (Recommended for MVP)
- Named users for managers/accounting/admin
- Shared station account for cashier terminals in early phase
- Move to fully named accounts before full production rollout

## MVP Process Scope
### In Scope
- Raw material receiving
- Supplier cost entry
- Recipe-driven production posting
- Finished goods stock updates
- Transfer to 3 stores by kg
- Store receive and movement entry
- Daily report generation

### Out of Scope
- Deep POS API integration
- Automated demand forecasting
- Multi-site manufacturing planning

## Role Permissions Matrix (MVP)
- Executive: view dashboard, approve major adjustments
- Factory Manager: approve production and stock adjustments
- Warehouse User: receive stock, issue materials, count inventory
- Production Supervisor: create/complete production orders
- Store User: receive transfers, enter daily movement, reconcile stock
- Accountant: view costs, margins, and valuation reports
- Admin: manage users, roles, configuration values

## MVP Governance Rules
- No user shares manager credentials
- Every stock adjustment requires reason code
- Every transfer requires dispatch and receipt confirmation
- End-of-day closure required at each store
