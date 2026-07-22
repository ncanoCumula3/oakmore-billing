"""
Invoice-line generator. Pure: takes resolved members + enrollments + catalog and
produces the itemized invoice, preserving the current/backbilled/credited member buckets
that payments and commissions depend on.
"""
from __future__ import annotations
from datetime import date

from .domain import Product, Enrollment, MemberCtx, LineItem, MemberInvoice, InvoiceResult
from .enums import Scope, LineType
from .rating import rate


def generate_invoice(
    client_id: int,
    service_month: date,
    members: list[MemberCtx],
    catalog: dict[str, Product],
    client_enrollments: list[Enrollment],       # scope ALL_MEMBERS or CLIENT_FLAT
    member_enrollments: dict[int, list[Enrollment]],  # member_id -> overrides/additions
) -> InvoiceResult:
    """
    For each active member, expand applicable products (client ALL_MEMBERS defaults +
    member-specific) into line items. CLIENT_FLAT products emit one member_id=None line.
    Member-level enrollment for a product_code overrides the client default for that member.
    """
    result = InvoiceResult(client_id=client_id, service_month=service_month)

    all_member_defaults = [e for e in client_enrollments if e.scope is Scope.ALL_MEMBERS]
    client_flat = [e for e in client_enrollments if e.scope is Scope.CLIENT_FLAT]

    # per-member line items
    for m in members:
        mi = MemberInvoice(member_id=m.member_id)
        overrides = {e.product_code: e for e in member_enrollments.get(m.member_id, [])}
        # union of product codes: client defaults + member-specific
        codes = list(dict.fromkeys(
            [e.product_code for e in all_member_defaults] + list(overrides.keys())
        ))
        for code in codes:
            enr = overrides.get(code) or next(
                (e for e in all_member_defaults if e.product_code == code), None
            )
            if enr is None:
                continue
            product = catalog[code]
            # bind the enrollment to this member
            bound = Enrollment(
                product_code=enr.product_code, scope=Scope.ALL_MEMBERS,
                unit_price=enr.unit_price, quantity=enr.quantity,
                member_id=m.member_id, effective_date=enr.effective_date, end_date=enr.end_date,
            )
            line = rate(product, bound, service_month, m.line_type)
            if line.amount != 0 or line.line_type is not LineType.CURRENT:
                mi.lines.append(line)
        if mi.lines:
            result.member_invoices.append(mi)

    # client-flat lines (member_id NULL) — always CURRENT
    if client_flat:
        flat_mi = MemberInvoice(member_id=None)
        for enr in client_flat:
            product = catalog[enr.product_code]
            flat_mi.lines.append(rate(product, enr, service_month, LineType.CURRENT))
        if flat_mi.lines:
            result.member_invoices.append(flat_mi)

    # preserve member-count buckets for commissions/payments
    result.current_member_count = sum(1 for m in members if m.line_type is LineType.CURRENT)
    result.backbilled_member_count = sum(1 for m in members if m.line_type is LineType.BACKBILLED)
    result.credited_member_count = sum(1 for m in members if m.line_type is LineType.CREDIT)
    return result


# --- deduction mirror -------------------------------------------------------
# maps product code -> the members.* column it projects onto
DEDUCTION_MIRROR = {
    "PCM_PRE_TAX": "pcm_pre_tax",
    "PCM_AFTER_TAX": "pcm_after_tax",
    "ADMIN_FEE_AFTER_TAX": "admin_fee_after_tax",
    "SIMRP_AFTER_TAX": "simrp_fee_after_tax",
}


def deduction_mirror(member_enrollments: list[Enrollment]) -> dict[str, str]:
    """
    Recompute the four members.* deduction columns from a member's product enrollments.
    Returns column -> value (str). The Products service writes this back on any enrollment change.
    """
    out = {col: "0.00" for col in DEDUCTION_MIRROR.values()}
    for enr in member_enrollments:
        col = DEDUCTION_MIRROR.get(enr.product_code)
        if col:
            out[col] = str((enr.unit_price * enr.quantity).quantize(__import__("decimal").Decimal("0.01")))
    return out
