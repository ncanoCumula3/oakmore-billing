"""
Rating strategies. Built now: FLAT (+ EMPLOYER/EMPLOYEE/SPLIT payer) with per-day proration.
Deferred models raise NotImplementedError but keep the dispatch shape.
"""
from __future__ import annotations
from datetime import date
from decimal import Decimal

from .domain import Product, Enrollment, LineItem, money
from .enums import PricingModel, Payer, LineType


def period_bounds(service_month: date) -> tuple[date, int]:
    """First day of month and number of days in that month."""
    import calendar
    days = calendar.monthrange(service_month.year, service_month.month)[1]
    return date(service_month.year, service_month.month, 1), days


def proration_factor(product: Product, service_month: date, enr: Enrollment) -> Decimal:
    """Per-day for prorate=True (active_days / days_in_month); 1 otherwise."""
    if not product.prorate:
        return Decimal("1")
    first, days_in_month = period_bounds(service_month)
    last = date(service_month.year, service_month.month, days_in_month)
    start = max(enr.effective_date or first, first)
    end = min(enr.end_date or last, last)
    if end < start:
        return Decimal("0")
    active_days = (end - start).days + 1
    return (Decimal(active_days) / Decimal(days_in_month))


def split_payer(product: Product, amount: Decimal) -> tuple[Decimal, Decimal]:
    """Return (employer_amount, employee_amount)."""
    if product.payer is Payer.EMPLOYER:
        return amount, Decimal("0.00")
    if product.payer is Payer.EMPLOYEE:
        return Decimal("0.00"), amount
    if product.payer is Payer.SPLIT:
        emp = money(amount * product.employer_split)
        return emp, money(amount - emp)
    return Decimal("0.00"), Decimal("0.00")  # NONE


def rate(product: Product, enr: Enrollment, service_month: date,
         line_type: LineType) -> LineItem:
    """Produce one line item for a member/client + product enrollment."""
    if product.pricing_model is not PricingModel.FLAT:
        raise NotImplementedError(f"pricing_model {product.pricing_model} not built yet")
    pf = proration_factor(product, service_month, enr)
    amount = money(enr.quantity * enr.unit_price * pf)
    employer_amt, employee_amt = split_payer(product, amount)
    return LineItem(
        product_code=product.code,
        description=product.name,
        line_type=line_type,
        quantity=enr.quantity,
        unit_price=enr.unit_price,
        proration_factor=pf,
        amount=amount,
        payer=product.payer,
        employer_amount=employer_amt,
        employee_amount=employee_amt,
        taxable=product.taxable,
        gl_account=product.gl_account,
        service_month=date(service_month.year, service_month.month, 1),
        member_id=enr.member_id,
    )
