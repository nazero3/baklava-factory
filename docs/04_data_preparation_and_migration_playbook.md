# Data Preparation and Migration Playbook

## Purpose
Prepare clean, reliable data so the system starts with accurate stock, recipes, and costing.

## Data Owners
- Operations Lead: product and recipe data
- Warehouse Lead: raw material and opening stock
- Accounting Lead: supplier costs and valuation rules
- Store Leads: opening stock per store
- Project Data Coordinator: final validation and upload control

## Data Sets Required
1. Products
2. Raw materials
3. Recipes (BOM) and expected yields
4. Suppliers
5. Stores and locations
6. User list and role mapping
7. Opening stock by lot and location
8. Optional historical movements (3-6 months)

## Standard Templates (CSV/Excel)
### Template A: Product Master
- ProductCode (unique)
- ProductName
- ProductType (Raw, Semi, Finished)
- BaseUnit (kg)
- ConversionRule (if needed)
- ActiveFlag

### Template B: Recipe/BOM
- RecipeCode (unique)
- FinishedProductCode
- IngredientProductCode
- IngredientQtyPer1KgOutput
- ExpectedYieldPercent
- EffectiveDate
- Version

### Template C: Supplier Master
- SupplierCode
- SupplierName
- Contact
- PaymentTerms
- Currency
- ActiveFlag

### Template D: Opening Stock
- LocationCode (Factory/Store1/Store2/Store3)
- ProductCode
- LotNumber
- QuantityKg
- UnitCost
- ExpiryDate (if applicable)
- StockDate

### Template E: User and Role Mapping
- FullName
- Username
- Role
- LocationAccess
- ApprovalLevel

## Data Quality Rules
- No duplicate codes
- No negative quantities
- No missing mandatory fields
- Only valid units and location codes
- Recipe ingredients must exist in product master
- Opening stock valuation method must match agreed costing rule

## Migration Steps
### Step 1: Collect
- Business owners fill templates and submit version 1

### Step 2: Validate
- Run data validation checks and issue a correction list

### Step 3: Correct
- Owners fix flagged records and resubmit version 2

### Step 4: Re-Validate
- Confirm error-free dataset and lock migration set

### Step 5: Dry Run
- Import into test environment and execute sample reports

### Step 6: Sign-Off
- Business confirms migrated totals and counts

### Step 7: Production Load
- Import approved final files before go-live

## Reconciliation Controls
- Compare opening stock totals by location before and after migration
- Check top 20 products by volume for quantity and cost match
- Validate 10 sample recipes with production supervisor

## Data Timeline (Typical)
- Week 1: Template distribution and first collection
- Week 2: Validation and corrections
- Week 3: Dry run and business sign-off
- Week 4: Final production load (aligned with go-live)

## Risks and Mitigations
- Late data submission -> weekly owner checkpoints
- Incorrect recipe yields -> supervised recipe validation workshop
- Cost discrepancies -> accounting-led valuation approval gate

## Exit Criteria
- All mandatory templates approved
- Validation errors closed
- Opening stock reconciled
- Sign-off from operations and accounting
