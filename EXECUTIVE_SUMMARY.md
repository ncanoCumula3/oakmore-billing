# Oakmore Billing Platform — Executive Summary

## The situation
We run a proven, multi‑tenant billing and administration platform (today "Member Manager" /
Attentive Members). It handles the full cycle for our clients: members and dependents, monthly
invoicing, payments and ACH, and broker commissions. It works and it is in production. But it is
built as a bespoke system on a technology stack that is harder to hire for, ties knowledge to a few
people, and was not designed to be sold or brandable as an Oakmore product. It also cannot yet put
**multiple product lines on an invoice** — a capability our clients and prospects increasingly ask
for.

## The proposal
Rebuild the platform, deliberately and incrementally, into an **Oakmore‑branded product**: one
modern, single‑language (Python) codebase, cleaner to operate and to hire for, ready to onboard new
clients quickly and to white‑label. We keep **100% of today's functionality** and add **itemized,
product‑line invoicing** as the headline new capability. Members and dependents are untouched.

## Why it matters
- **Turns a system into a product.** Brandable, self‑serve client onboarding, and a foundation we
  can sell or white‑label — not just operate for ourselves.
- **Closes a real gap.** Product‑line invoicing is a concrete customer request; it broadens what we
  can bill and win.
- **Reduces risk.** One consistent, typed, modern stack lowers key‑person and platform risk and
  makes the team easier to grow.
- **Same economics.** It runs on our current hosting with a minimal operational footprint
  (effectively just the application and its database).

## How we de‑risk it
This is **not a big‑bang rewrite.** We stand the new platform up beside the current one and migrate
one area at a time, running both in parallel. Before anything switches over, we prove the new system
reproduces the old invoices and commissions **to the cent, per client.** We reuse what already works
(login and email systems stay as they are). Value lands in stages, with checkpoints — not as a
single all‑or‑nothing bet.

## What it will take
Indicative planning estimate: a small team (roughly 3–5 engineers) over about 9–12 months, delivered
in phases so functionality and decision points arrive along the way. Incremental infrastructure cost
is low because it reuses our existing hosting and shared services.

## Where we are today
The foundation is already proven. The new billing engine — including the itemized product‑line
logic — is built and tested, and it **reproduces our real invoice numbers exactly.** That retires
the biggest technical unknown before we commit further.

## The decision
We recommend approving the first phases (foundations and the first live client area) with a formal
checkpoint after the parity proof against production data. That keeps the commitment staged: we
confirm it works on real numbers before scaling the investment.
