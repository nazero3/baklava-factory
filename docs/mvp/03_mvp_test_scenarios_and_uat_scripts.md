# MVP Test Scenarios and UAT Scripts

## Test Objective
Validate that the MVP works correctly for the most critical business operations.

## Test Execution Rules
- Record tester name, date, and environment
- Use controlled test data set
- Capture evidence (screenshots or exported report)
- Every failed case must include root cause and owner

## UAT Scenario List

## Scenario 1: Raw Material Receiving
### Precondition
- Supplier exists
- Raw material exists

### Steps
1. Create purchase/receiving entry
2. Enter lot, quantity kg, and unit cost
3. Submit transaction

### Expected Result
- Stock increases in raw inventory
- Ledger records receiving entry
- Cost updates correctly

## Scenario 2: Production Order with Recipe Consumption
### Precondition
- Recipe active
- Raw materials available

### Steps
1. Create production order for selected baklava product
2. Enter target output kg
3. Post production completion

### Expected Result
- Ingredients consumed according to recipe
- Finished goods increased by actual output kg
- Waste/loss captured if entered

## Scenario 3: Transfer to Store
### Precondition
- Finished goods available in factory

### Steps
1. Create transfer note to Store 1
2. Dispatch transfer
3. Receive transfer at Store 1

### Expected Result
- Factory stock decreases
- Store stock increases after receipt
- Transfer status updates to received

## Scenario 4: Store Daily Movement
### Precondition
- Store has available stock

### Steps
1. Enter daily sales movement
2. Enter returns and waste if any
3. Close day reconciliation

### Expected Result
- Net store stock reflects all movements
- Day closure report available

## Scenario 5: Stock Count and Adjustment
### Precondition
- Existing book stock

### Steps
1. Start cycle count for selected items
2. Enter physical count
3. Submit variance adjustment for approval

### Expected Result
- Variance calculated correctly
- Approval flow triggered above threshold
- Audit log records change

## Scenario 6: KPI Dashboard and Margin Report
### Precondition
- At least one full business cycle completed

### Steps
1. Open dashboard
2. Open daily margin report
3. Filter by store and product

### Expected Result
- KPI values render successfully
- Margin data is available and traceable to transactions

## UAT Sign-Off Criteria
- 100% of critical scenarios passed
- No unresolved critical defects
- High defects have approved workaround and closure date
- Business sponsor signs acceptance record

## Defect Severity Rules
- Critical: blocks core flow or causes incorrect stock/cost totals
- High: major issue with workaround
- Medium: non-blocking issue with moderate impact
- Low: cosmetic or minor usability issue
