# Products Service (Oakmore Billing)

FastAPI + SQLAlchemy 2.0 (typed) + Pydantic v2. Python + Postgres only. DB-per-tenant.
Adds the product catalog and **product lines per invoice**; reproduces today's fee numbers.

## Layout
```
app/enums.py       domain enums (PricingModel, Payer, Scope, LineType, ...)
app/domain.py      pure DB-free objects (Product, Enrollment, LineItem, InvoiceResult)
app/rating.py      FLAT + split rating, per-day proration   (built now)
app/generator.py   invoice-line generator + current/backbilled/credited buckets + deduction mirror
app/models.py      SQLAlchemy typed models (billing schema)
app/schemas.py     Pydantic v2 DTOs (contracts)
app/db.py          DB-per-tenant routing (X-Company-Id -> DSN)
app/main.py        FastAPI: /products, /invoices/preview-lines
migrations/001_init.sql   DDL for the billing schema (per tenant DB)
tests/test_products.py    parity/proration/split/mirror/bucket tests (all green)
```

## Run
```
pip install -e ".[dev]"
python -m pytest                                   # unit tests (no DB needed)
export TENANT_ATTENTIVE_DATABASE_URL=postgresql://...   # a tenant DB
psql "$TENANT_ATTENTIVE_DATABASE_URL" -f migrations/001_init.sql
uvicorn app.main:app --reload
# preview:
curl -X POST localhost:8000/invoices/preview-lines -H 'X-Company-Id: 3' \
     -H 'content-type: application/json' -d '{"client_id":1484,"service_month":"2026-07-01"}'
```

## What's built vs deferred
- Built: FLAT pricing, EMPLOYER/EMPLOYEE/SPLIT payer, per-day proration (prorate=true) / flat monthly,
  client-flat lines (member_id NULL), member-count buckets for commissions, deduction mirror.
- Deferred (interface reserved): PER_MEMBER, PER_DEPENDENT, TIERED, PERCENTAGE (base parked).

## Notes
- Auth is delegated to the reused core-auth service (validate bearer at the gateway).
- Active-member resolution reads the Accounts read model (members + member_status) in the tenant DB;
  in the full topology this is the Accounts service.
- The deduction mirror keeps members.{pcm_pre_tax,pcm_after_tax,admin_fee_after_tax,simrp_fee_after_tax}
  as a projection so the existing Deductions tab and reports keep working.
