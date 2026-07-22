# Oakmore Billing — Competitive Feature Review

Two markets touch this product: **benefits‑admin / TPA platforms** (Employee Navigator, Ease,
PlanSource, TPA Stream, DataPath, PLEXIS) and **modern billing platforms** (Stripe Billing,
Chargebee, Maxio, Recurly). We sit in the middle: benefits/TPA billing with a real invoice + ACH +
commission engine. This maps what we have, what they have, and what to build.

## What we have (verified)
- Clients, members + dependents, member status lifecycle, member import.
- **Product catalog + itemized invoices (new, live)** — FLAT + split payer, per‑day proration,
  client‑flat lines, deduction mirror. Real invoices generate (e.g. Reliant Care $1.12M, 3,009 lines).
- Invoicing (draft→final, adjustments), public invoice viewer/link.
- Payments + ACH/NACHA; broker commissions (runs, adjustments, broker ACH).
- Multi‑tenant (DB‑per‑tenant), RBAC (external auth), Knit payroll sync, reports.

## Feature comparison
| Capability | Us | Ben‑admin/TPA peers | Modern billing (Stripe/Chargebee/Maxio) |
|---|---|---|---|
| Product catalog / itemized invoice | ✅ new | partial (fees/plans) | ✅ mature |
| Pricing models (tiered/volume/per‑unit/usage/prepaid/hybrid) | ⛔ FLAT only (rest deferred) | limited | ✅ full |
| Proration on mid‑cycle change | ✅ per‑day | some | ✅ |
| Discounts / coupons / credits / grandfathering | ⛔ (only adjustments) | limited | ✅ |
| Tax automation (US sales tax / VAT via Avalara) | ⛔ (fields only) | some | ✅ |
| Dunning (reminders, smart retries) | ⛔ | some | ✅ |
| Revenue recognition (ASC 606 / IFRS 15) | ⛔ | rare | ✅ (Chargebee/Maxio) |
| Online payment on hosted invoice (card + ACH) | ⛔ (ACH pull only) | ✅ portals | ✅ |
| Consolidated/flexible cadence (monthly/qtr/advance/arrears) | partial | ✅ (TPA Stream) | ✅ |
| White‑label employer/broker portal + self‑service | ⛔ (viewer only) | ✅ | ✅ (customer portal) |
| Commissions (broker/agency) | ✅ | ✅ | ⛔ (not their domain) |
| Payroll sync (Knit/Paycor) | ✅ | ✅ | ⛔ |
| Enrollment / open enrollment / plan shopping | ⛔ | ✅ (Employee Navigator/Ease) | ⛔ |
| ACA compliance / 1094‑1095 | ⛔ | ✅ | ⛔ |
| Carrier EDI 834 feeds | ⛔ | ✅ | ⛔ |
| API + webhooks / integration marketplace | partial | ✅ (300+ partners) | ✅ |
| AR aging / collections / analytics | partial (reports) | some | ✅ |

Our edge vs pure billing platforms: **commissions + payroll sync + member/dependent model**. Our
gaps vs both: **pricing flexibility, payments/dunning, tax, self‑service portals, and integrations**.

## What to implement, prioritized — and how (our stack: FastAPI + Postgres + Reflex on Render)

### Tier 1 — billing flexibility & getting paid (near‑term, highest leverage)
1. **Finish the pricing models** (tiered, volume, per‑member, percentage) behind the existing
   `rate()` strategy interface. *How:* one typed strategy each in the Products service; data‑driven
   via `product_prices.tier_json`. Small, isolated, testable.
2. **Discounts / credits / grandfathering.** *How:* a `discounts` table + a rating step; credits as
   negative line items (we already support line types).
3. **Online invoice payment (card + ACH) on the hosted invoice.** *How:* a Payments service
   integrating **Stripe** (cards + ACH debit) or Authorize.net; extend the public invoice viewer to
   "Pay now"; reconcile back to `client_payments`. This closes collections, not just ACH pull.
4. **Dunning.** *How:* Procrastinate scheduled jobs (Postgres) → reminder emails via the reused
   dispatch + payment retries; a `dunning_state` per invoice. No new infra.
5. **Tax.** *How:* start with a US sales‑tax rate table keyed by jurisdiction (fields already on
   products); upgrade to **Avalara** integration when needed.

### Tier 2 — product & platform
6. **White‑label employer + broker self‑service portals.** *How:* Reflex apps/roles reading the
   services; per‑tenant branding from tenant‑config. Extends the invoice viewer into a real portal.
7. **Flexible invoice cadence** (monthly/quarterly/advance/arrears) + **consolidated invoicing.**
   *How:* schedule config per client on the invoice‑process; the generator already itemizes.
8. **AR aging / collections dashboard + analytics.** *How:* a Reporting service + Reflex dashboards
   over invoices/payments.
9. **API keys + webhooks + integration SDK.** *How:* gateway issues per‑tenant API keys; an events
   service publishes webhooks from the outbox. Opens the partner ecosystem.

### Tier 3 — benefits‑admin depth (if we chase Employee Navigator/Ease territory)
10. **Enrollment / open enrollment / plan shopping**, **ACA 1094/1095**, **EDI 834 carrier feeds.**
    *How:* an Enrollment service + a Compliance service + an EDI integration service. Larger; pursue
    only if we position as full ben‑admin, not just billing.

### Cross‑cutting to reach parity with billing platforms
- **Revenue recognition (ASC 606)** for finance customers — a rev‑rec module over invoice lines.
- **Multi‑currency** if we go beyond US.

## Recommended sequence
Ship Tier 1 first (pricing models → online payment + dunning → tax): it makes billing flexible and
gets money in, which is the point of the product, and it's all inside our current services with no
new infrastructure. Tier 2 turns it into a self‑service product. Tier 3 only if we compete head‑on
with the ben‑admin suites.

## Sources
- Benefits‑admin / TPA billing features: TPA Stream consolidated invoicing, DataPath, PLEXIS,
  Employee Navigator / Ease / PlanSource.
- Modern billing feature sets: Stripe Billing, Chargebee, Maxio, Recurly (pricing models, dunning,
  tax, rev‑rec).
