"""Runnable tests for rating + generator + mirror. `python -m pytest` or run directly."""
from __future__ import annotations
from datetime import date
from decimal import Decimal
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.enums import PricingModel, Payer, Scope, LineType
from app.domain import Product, Enrollment, MemberCtx, money
from app.rating import rate, proration_factor
from app.generator import generate_invoice, deduction_mirror

# --- a standard product catalog (the current fees expressed as products) ---
CATALOG = {
    "EMPLOYER_FEE":        Product("EMPLOYER_FEE", "Employer Fee", PricingModel.FLAT, Payer.EMPLOYER, sort_order=10),
    "EMPLOYEE_FEE":        Product("EMPLOYEE_FEE", "Employee Fee", PricingModel.FLAT, Payer.EMPLOYEE, sort_order=20),
    "ADMIN_FEE_AFTER_TAX": Product("ADMIN_FEE_AFTER_TAX", "Admin Fee After Tax", PricingModel.FLAT, Payer.EMPLOYER, sort_order=30),
    "PCM_PRE_TAX":         Product("PCM_PRE_TAX", "PCM Pre Tax", PricingModel.FLAT, Payer.EMPLOYEE, sort_order=40),
    "PCM_AFTER_TAX":       Product("PCM_AFTER_TAX", "PCM After Tax", PricingModel.FLAT, Payer.EMPLOYEE, sort_order=50),
    "SIMRP_AFTER_TAX":     Product("SIMRP_AFTER_TAX", "SIMRP After Tax", PricingModel.FLAT, Payer.EMPLOYEE, sort_order=60),
    # a prorated, split product to exercise those paths
    "SUPP_SPLIT":          Product("SUPP_SPLIT", "Supp (split)", PricingModel.FLAT, Payer.SPLIT, prorate=True,
                                   employer_split=Decimal("0.5"), sort_order=70),
}
JULY = date(2026, 7, 1)


def enr(code, price, member_id=None, scope=Scope.ALL_MEMBERS, qty="1", eff=None, end=None):
    return Enrollment(code, scope, Decimal(price), Decimal(qty), member_id, eff, end)


def test_flat_split_and_payer_routing():
    p = CATALOG["SUPP_SPLIT"]
    line = rate(p, enr("SUPP_SPLIT", "100.00", member_id=1), JULY, LineType.CURRENT)
    assert line.amount == Decimal("100.00")
    assert line.employer_amount == Decimal("50.00")
    assert line.employee_amount == Decimal("50.00")
    # employer-only product
    e = rate(CATALOG["EMPLOYER_FEE"], enr("EMPLOYER_FEE", "41.08", member_id=1), JULY, LineType.CURRENT)
    assert (e.employer_amount, e.employee_amount) == (Decimal("41.08"), Decimal("0.00"))


def test_per_day_proration():
    p = CATALOG["SUPP_SPLIT"]  # prorate=True
    # active July 17..31 => 15 of 31 days
    line = rate(p, enr("SUPP_SPLIT", "310.00", member_id=1, eff=date(2026, 7, 17)), JULY, LineType.CURRENT)
    assert proration_factor(p, JULY, enr("SUPP_SPLIT", "310.00", member_id=1, eff=date(2026, 7, 17))) == Decimal(15) / Decimal(31)
    assert line.amount == money(Decimal("310.00") * (Decimal(15) / Decimal(31)))  # 150.00
    # non-prorated product ignores mid-month start
    full = rate(CATALOG["EMPLOYER_FEE"], enr("EMPLOYER_FEE", "41.08", member_id=1, eff=date(2026, 7, 17)), JULY, LineType.CURRENT)
    assert full.amount == Decimal("41.08")


def test_itemized_invoice_parity():
    """A member with the four deduction products reproduces the known totals (Electric Shop-style)."""
    members = [MemberCtx(member_id=32, line_type=LineType.CURRENT)]
    member_enr = {32: [
        enr("PCM_PRE_TAX", "541.38", 32),
        enr("PCM_AFTER_TAX", "84.94", 32),
        enr("ADMIN_FEE_AFTER_TAX", "41.08", 32),
        enr("SIMRP_AFTER_TAX", "541.38", 32),
    ]}
    inv = generate_invoice(client_id=1, service_month=JULY, members=members,
                           catalog=CATALOG, client_enrollments=[], member_enrollments=member_enr)
    mi = inv.member_invoices[0]
    amounts = {l.product_code: l.amount for l in mi.lines}
    assert amounts == {
        "PCM_PRE_TAX": Decimal("541.38"), "PCM_AFTER_TAX": Decimal("84.94"),
        "ADMIN_FEE_AFTER_TAX": Decimal("41.08"), "SIMRP_AFTER_TAX": Decimal("541.38"),
    }
    assert mi.total_fee == Decimal("1208.78")            # sum of the four lines
    assert inv.total_fee == Decimal("1208.78")


def test_client_flat_line_has_null_member():
    client_flat = [enr("ADMIN_FEE_AFTER_TAX", "1125.00", scope=Scope.CLIENT_FLAT)]
    inv = generate_invoice(1, JULY, [MemberCtx(1)], CATALOG, client_flat, {})
    flat = [mi for mi in inv.member_invoices if mi.member_id is None]
    assert len(flat) == 1
    assert flat[0].lines[0].member_id is None
    assert flat[0].total_fee == Decimal("1125.00")


def test_member_buckets_preserved_for_commissions():
    members = [MemberCtx(1, LineType.CURRENT), MemberCtx(2, LineType.CURRENT),
               MemberCtx(3, LineType.BACKBILLED), MemberCtx(4, LineType.CREDIT)]
    defaults = [enr("EMPLOYEE_FEE", "10.00")]
    inv = generate_invoice(1, JULY, members, CATALOG, defaults, {})
    assert inv.current_member_count == 2
    assert inv.backbilled_member_count == 1
    assert inv.credited_member_count == 1


def test_deduction_mirror():
    mirror = deduction_mirror([
        enr("PCM_PRE_TAX", "541.38", 32),
        enr("SIMRP_AFTER_TAX", "541.38", 32),
        enr("ADMIN_FEE_AFTER_TAX", "41.08", 32),
    ])
    assert mirror == {"pcm_pre_tax": "541.38", "pcm_after_tax": "0.00",
                      "admin_fee_after_tax": "41.08", "simrp_fee_after_tax": "541.38"}


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn(); print("PASS", fn.__name__)
    print(f"\nall {len(fns)} tests passed")
