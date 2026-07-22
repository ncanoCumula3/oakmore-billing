# Oakmore Billing — What We're Building (Discussion Doc)

## What we want to build
An Oakmore‑owned billing and administration platform: the same job Member Manager does today —
clients, members and dependents, monthly invoicing, payments and ACH, broker commissions, payroll
sync — rebuilt as a clean, all‑Python, multi‑tenant product we can brand, onboard clients into
quickly, and eventually white‑label or sell. The one functional addition is **product lines on an
invoice**: instead of a single fixed fee per member, an invoice becomes itemized, with a real
product catalog behind it.

Nothing about members or dependents changes. Everything Member Manager does, this does — plus the
catalog and itemized invoicing, on a platform built to be a product rather than a bespoke system.

## How it's different from Member Manager
Member Manager is a bespoke application: NestJS on the back, Angular on the front, one large codebase
per tenant, with invoicing hard‑wired to a single per‑member fee. It works, but it wasn't built to
be branded, sold, or grown by a larger team, and it can't itemize an invoice.

Oakmore Billing keeps the exact same domain and behavior, but changes four things:
- **One language, end to end (Python).** Back and front. Typed throughout.
- **Microservices instead of one monolith** — each area (accounts, products, invoicing, payments,
  commissions…) is its own service with clear ownership, deployed independently.
- **A product catalog and itemized invoices** — the functional new capability.
- **Built to be a product** — Oakmore‑branded, self‑serve tenant onboarding, white‑label ready.

Same isolation model as today: **one database per tenant.** Same login and email systems (we reuse
them). So the delta is the stack, the itemized billing, and the productization — not a new feature
set and not a change to how members work.

## How items (product lines) integrate
This is the part that matters most, because it has to slot in without disturbing anything.

Today an invoice is effectively one bundle per member: an employer fee, an employee fee, a total,
and the deduction fields (PCM pre/after, SIMRP, admin) that live on the member record.

In the new model, an **invoice item is a product applied to a member.** We add a per‑tenant product
catalog, let each member (or client) be enrolled in one or more products, and the invoice generator
expands those enrollments into **line items** — one line per product per member, plus client‑level
flat lines where needed.

The integration is deliberately additive:
- **Existing fees become products.** Employer fee, employee fee, admin, PCM, SIMRP are seeded as
  standard products. Run the new generator and it reproduces today's invoices **to the cent** — we
  test exactly that.
- **The invoice totals are unchanged in shape.** Line items roll up into the same employer/employee/
  total figures the rest of the system already reads.
- **Payments and commissions are untouched.** They depend on per‑member current/backbilled/credited
  counts, and the generator keeps emitting those alongside the new lines.
- **The deduction fields stay live.** The four member columns become a mirror kept in sync from the
  product enrollments, so the Deductions screen and every report keep working unchanged.

So "items" are a layer on top of the current invoice engine, not a replacement. You get itemization
and a catalog; nothing downstream breaks.

## Why Python
- **The heavy pieces are already Python.** ACH/NACHA file generation and the report builders run in
  Python today. We build on that rather than around it.
- **One language front to back.** Reflex lets the UI be Python too, so the team works in a single
  stack with shared, typed contracts — less surface area, easier to hire for and grow.
- **Type safety for money.** Pydantic and typed SQLAlchemy with strict checking give us correctness
  guarantees where it counts — invoice and commission math.
- **Less to run.** The new services need only Python and Postgres. Background work, queues, and events
  are done on Postgres itself, so there's no extra infrastructure (no Temporal, Kafka, or Redis in the
  new services) to operate or pay for.

## The rest (the reasoning behind the other choices)
- **Microservices from day one, one repo.** Clear ownership per area; a shared core library and
  generated typed clients keep the cost of many services low.
- **DB‑per‑tenant.** Keeps today's hard isolation and maps one‑to‑one to a Postgres per tenant.
  Services share the tenant's database but each owns its own schema, so there's no database sprawl.
- **Reuse auth and email.** Login (core‑auth) and the email dispatch already work; we call them, we
  don't rebuild them. The email system's use of Temporal stays inside that service.
- **Reflex for the UI.** A real single‑page app, written in Python, kept as its own tier that talks
  to the gateway — so front and back stay cleanly separated.
- **Render for hosting.** Same platform we use now; one blueprint file describes every service.
- **Move without a big‑bang.** We stand the new platform up beside the current one, migrate one area
  at a time, run both in parallel, and only cut a client over after the new numbers match the old to
  the cent. Auth and email never move.

## What the product does (feature list)
Clients and members + dependents · member status lifecycle and the "current member" display rule ·
member import (xlsx/csv) · comments, tags, histories · **product catalog and itemized invoices
(new)** · monthly invoice runs (draft → final) · invoice adjustments · public invoice viewer/link ·
client payments and application to invoices · bank accounts and ACH/NACHA · broker commissions (runs,
adjustments, broker ACH) · brokers, agencies, account managers, commission rates · Knit payroll
integration · enrollment/custom/invoice/commission reports (XLSX/PDF) · multi‑tenant, RBAC, file
storage, self‑serve onboarding, Oakmore branding.

## Where we are
The billing engine, including the itemized product‑line logic, is already built and tested and
reproduces our real invoice numbers exactly. That's the piece with the most risk, and it's proven.
Next is the parity migration on real tenant data, then the catalog/enrollment APIs, then the UI.
