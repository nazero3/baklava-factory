# Baklava Factory MVP Backend

This is the first working MVP backend implementation aligned with the project documents.

## Included Business Flows
- Raw material receiving
- Recipe-based production completion
- Factory-to-store transfer dispatch/receive
- Store movement (sale, return, waste)
- Inventory view and daily KPI summary
- Authentication and role-based authorization
- Approval workflow for large stock adjustments and transfer discrepancies
- CSV import/export for products and store movements

## Tech Stack
- FastAPI
- SQLite
- SQLAlchemy
- Pytest

## Run Locally
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API docs:
- `http://127.0.0.1:8000/docs`

Default bootstrap admin (MVP only):
- Username: `admin`
- Password: `admin123`

## Run Tests
```bash
pytest -q
```

## Notes
- Database file: `mvp.db` in project root
- This is MVP foundation code; next phase can add stronger security controls, full approvals engine, and richer analytics
