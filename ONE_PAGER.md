# Oakmore Billing — One‑Pager

**What.** Rebuild the Attentive Members / Member Manager app as an Oakmore‑branded product, keeping
100% of today's features and adding **product lines per invoice**. Members and dependents are
unchanged; invoices become itemized.

**Why now.** The app is a working multi‑tenant TPA billing platform (NestJS + Angular). Productizing
it means a clean, typed, all‑Python codebase, an editable product catalog, and itemized invoices —
without losing the invoicing, payments/ACH, commissions, payroll‑sync, or reporting that exist today.

## Decisions & rationale
| Decision | Rationale |
|---|---|
| **100% Python**, front and back | One language for the team; the ACH/NACHA + report generators are already Python. |
| Back end: **FastAPI + SQLAlchemy 2.0 (typed) + Pydantic v2** | Async, OpenAPI out of the box, end‑to‑end types (replaces NestJS/Prisma). |
| Front end: **Reflex** (Python → React) | 100% Python SPA with real routing/state; stays a separate tier calling the gateway. |
| **Python + Postgres only** in new services | Minimal ops surface. Jobs = Procrastinate (Postgres queue); events = transactional outbox + LISTEN/NOTIFY. No Temporal/Kafka/Redis inside the new services. |
| **Full microservices from day one** (~11) | Clear ownership/scaling per bounded context; one repo + shared libs keep it cheap. |
| **DB‑per‑tenant** (one Postgres per tenant) | Keeps today's isolation model and maps 1:1 to Render Postgres. Services share the tenant DB via **schema‑per‑service** (no DB explosion). |
| **Type‑safe** end to end | `pyright --strict`, shared `oakmore-contracts` (Pydantic DTOs), OpenAPI‑generated clients so services + Reflex share one contract. |
| **Reuse core‑auth + the Temporal email dispatch** | Don't rebuild working platform services; call them over HTTP. Temporal stays encapsulated inside the email service, so the "no Temporal" rule holds for the new services. |
| **Deploy on Render** via `render.yaml` | Current hosting; Blueprint defines gateway + services + workers + Reflex; Postgres per tenant provisioned by the Tenant service. |
| Migration: **strangler‑fig, not big‑bang** | Stand up Python beside the old stack, move one context at a time, parallel‑run, cut over per tenant. |
| **Golden‑data parity gate** per module | An old module is retired only after new vs old invoice/commission totals match to the cent per tenant. |

## The product change (product lines per invoice)
Per‑tenant **product catalog** + **member/client product enrollment**; the generator expands each
member's products into **invoice_line_items**. Today's employer/employee/admin/PCM/SIMRP fees become
standard products so existing invoices reproduce exactly.

Billing decisions: **FLAT + split payer** built now; **PERCENTAGE parked** (PER_MEMBER/PER_DEPENDENT/
TIERED deferred behind the interface). **Client‑flat** lines sit on `invoices_final` with
`member_id` NULL. The four member deduction columns become a **permanent mirrored read model**
projected from `member_products` (Deductions tab + reports keep working). Proration is **per‑day**
for `prorate=true`, flat monthly otherwise. **Non‑negotiable:** the generator keeps emitting per‑member
current/backbilled/credited counts, because payments and commissions depend on them.

## Services (~11)
Tenant/Provisioning · Accounts (Clients & Members) · Brokers & Distribution · **Products & Catalog
(new)** · Invoicing (itemized) · Payments & ACH · Commissions · Integrations (Knit) · Reporting ·
Files — all calling **reused** core‑auth + email dispatch.

## Plan (strangler‑fig, ~9–12 months, FE/BE in parallel)
0 Foundations → 1 Platform core (tenant provisioning, Postgres queue/outbox) → 2 Accounts →
3 Products & invoice lines → 4 Invoicing & Payments → 5 Commissions → 6 Reflex FE to parity →
7 Integrations & Reporting → 8 per‑tenant cutover.

## Status
Products service scaffolded, wired, and **tested (6/6, incl. a to‑the‑cent parity test)** at
`/Users/nico/oakmore-billing/`. Next: parity migration + golden‑data reconciliation against the
current `get_invoice_data_inv()`, then catalog/enrollment API, then the Reflex UI.

*Detail: PRODUCT_ROADMAP.md · PRODUCTS_DESIGN.md · ARCHITECTURE.md (in /Users/nico/Downloads/mm_export/).*
