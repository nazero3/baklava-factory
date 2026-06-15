# MVP API Quick Reference

## Base
- Local URL: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`

## Health
- `GET /health`

## Authentication and Users
- `POST /auth/login`
- `GET /auth/me`
- `POST /auth/users` (admin only)

## Master Data
- `POST /suppliers`
- `POST /stores`
- `POST /products`
- `POST /recipes`

## Operations
- `POST /receivings`
- `POST /production/batches/complete`
- `POST /transfers/dispatch`
- `POST /transfers/{transfer_id}/receive`
- `POST /stores/{store_id}/movements`
- `POST /inventory/adjustments`
- `POST /inventory/adjustments/{adjustment_id}/approve`
- `POST /transfer-exceptions/{exception_id}/approve`

## Visibility
- `GET /inventory`
- `GET /dashboard/daily-summary`

## CSV Import/Export
- `POST /import/products-csv`
- `POST /import/store-movements-csv`
- `GET /export/products-csv`
- `GET /export/daily-summary-csv`

## Minimal Run Commands
```bash
cd mvp_backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Minimal Test Command
```bash
cd mvp_backend
source .venv/bin/activate
pytest -q
```

## Default MVP Admin
- Username: `admin`
- Password: `admin123`
