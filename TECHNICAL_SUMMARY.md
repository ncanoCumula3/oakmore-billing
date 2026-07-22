# Oakmore Billing — Technical Summary

Rebuild Member Manager (NestJS + Angular) into an Oakmore product: all‑Python microservices,
type‑safe, multi‑tenant, with **product lines per invoice** added. Keep every current feature.

## What we're building
- **Back end:** FastAPI services, SQLAlchemy 2.0 (typed), Pydantic v2, Alembic. `pyright --strict`.
- **Front end:** Reflex (Python → React), Oakmore‑branded, separate tier calling the gateway.
- **Runtime: Python + Postgres only.** Jobs = Procrastinate (Postgres queue). Events = transactional
  outbox + LISTEN/NOTIFY. No Temporal/Kafka/Redis in the new services.
- **Full microservices from day one** (~11), one repo, shared `oakmore-core` + `oakmore-contracts`
  (Pydantic DTOs → OpenAPI → generated typed clients, so services and Reflex share one contract).
- **Reuse, don't rebuild:** existing **core‑auth** (authn/RBAC) and the **Temporal email dispatch**.
  Called over HTTP; Temporal stays inside the email service.
- **Multi‑tenant: DB‑per‑tenant.** One Render Postgres per tenant; each service owns a **schema**
  inside the tenant DB (databases = tenants, schemas = services). Tenant resolved at the gateway from
  the JWT / `X‑Company‑Id`, DSN selected per request.
- **Deploy: Render** via one `render.yaml` (gateway + services + workers + Reflex). Tenant service
  provisions each tenant's Postgres and runs per‑service Alembic migrations.

## Services
Gateway · Tenant/Provisioning · Accounts (Clients & Members) · Brokers & Distribution ·
**Products & Catalog (new)** · Invoicing (itemized) · Payments & ACH · Commissions ·
Integrations (Knit) · Reporting · Files.

## How we migrate (no big‑bang)
Strangler‑fig: stand the Python platform up beside the current app, move one context at a time,
parallel‑run per tenant, and gate each cutover on **to‑the‑cent reconciliation** of new vs old
invoice/commission totals (`get_invoice_data_inv()`). Reuse auth/email so those never move. Retire
NestJS/Angular tenant by tenant.

## The one functional change: product lines per invoice
- New tables (`billing` schema): `products`, `product_prices`, `client_products`, `member_products`,
  `invoice_line_items`.
- Members enroll in one or more products; the generator expands them into invoice line items.
- Today's employer/employee/admin/PCM/SIMRP fees become standard products → **existing invoices
  reproduce exactly.**
- **FLAT + split payer** built now; per‑day proration (`prorate=true`) else flat monthly.
  PERCENTAGE parked; PER_MEMBER/PER_DEPENDENT/TIERED deferred behind the same interface.
- Client‑flat lines live on `invoices_final` with `member_id` NULL.
- The four member deduction columns (`pcm_pre_tax`, `pcm_after_tax`, `admin_fee_after_tax`,
  `simrp_fee_after_tax`) become a **mirrored read model** projected from `member_products`, so the
  Deductions tab and reports keep working.
- The generator still emits per‑member **current/backbilled/credited** counts — payments and
  commissions read those, so they're untouched.

## Features in the product
**Accounts** — clients (employers); members + dependents; member status lifecycle
(ACTIVE/PENDING/TERM/ON LEAVE/OPTED_OUT, effective‑dated, soft‑invalidation, "current" display rule);
member import (xlsx/csv); change‑client; comments; tags; histories.

**Products & Billing (new)** — per‑tenant product catalog; effective‑dated pricing; client‑ and
member‑level enrollment with overrides; itemized invoices (product lines per member + client‑flat
lines); deduction mirror.

**Invoicing** — monthly invoice runs; draft → final; per‑member and per‑line adjustments; public
invoice viewer + link (with a sane token TTL, fixing today's 24h expiry).

**Payments & ACH** — client payments; apply‑to‑invoice with current/backbilled/credited splits;
bank accounts; NACHA/ACH file generation.

**Commissions** — commission runs (Calculated → Approved → Submitted → Paid); lines from cleared
payments × broker rate (PEPM); adjustments with approval; broker ACH payouts.

**Brokers & Distribution** — brokers, agencies, account managers; client↔broker relationships;
commission‑rate management + history.

**Integrations** — Knit payroll sync (Paycor/ADP/Paychex/BambooHR/Paylocity/QuickBooks).

**Reporting** — enrollment, custom, invoice‑summary, commission reports; XLSX/PDF export.

**Platform** — multi‑tenant (DB‑per‑tenant); RBAC (`resource:action`) via reused core‑auth; email
via reused dispatch; file storage; self‑serve tenant provisioning; Oakmore branding / white‑label.

## Status
Products service built and tested — pure billing core is **6/6 green incl. a to‑the‑cent parity
test** (four deduction products → 541.38 / 84.94 / 41.08 / 541.38, total 1208.78); FastAPI wiring,
migration DDL, and the Render blueprint in place at `/Users/nico/oakmore-billing/`.
Next: parity migration + golden‑data reconciliation, catalog/enrollment API, then the Reflex UI.
