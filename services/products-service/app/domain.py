"""
Pure, DB-free domain objects for rating + invoice-line generation.
These are the inputs the data layer resolves and the outputs it persists,
kept independent so the rating logic is unit-testable without Postgres.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

from .enums import PricingModel, Payer, Scope, LineType

TWO = Decimal("0.01")


def money(x: Decimal | int | float | str) -> Decimal:
    """Quantize to cents, banker-safe half-up."""
    from decimal import ROUND_HALF_UP
    return Decimal(str(x)).quantize(TWO, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class Product:
    code: str
    name: str
    pricing_model: PricingModel
    payer: Payer
    taxable: bool = False
    gl_account: str | None = None
    prorate: bool = False
    sort_order: int = 100
    # split fraction to the EMPLOYER when payer == SPLIT (0..1)
    employer_split: Decimal = Decimal("0")


@dataclass(frozen=True)
class Enrollment:
    """A member's or client's product enrollment for the period."""
    product_code: str
    scope: Scope
    unit_price: Decimal            # resolved price (override -> price row -> default)
    quantity: Decimal = Decimal("1")
    member_id: int | None = None   # None for CLIENT_FLAT
    effective_date: date | None = None
    end_date: date | None = None


@dataclass(frozen=True)
class MemberCtx:
    """A member and which billing bucket it falls in for this run."""
    member_id: int
    line_type: LineType = LineType.CURRENT   # CURRENT | BACKBILLED | CREDIT


@dataclass
class LineItem:
    product_code: str
    description: str
    line_type: LineType
    quantity: Decimal
    unit_price: Decimal
    proration_factor: Decimal
    amount: Decimal
    payer: Payer
    employer_amount: Decimal
    employee_amount: Decimal
    taxable: bool
    gl_account: str | None
    service_month: date
    member_id: int | None = None

    def as_row(self) -> dict:
        return {
            "member_id": self.member_id,
            "product_code": self.product_code,
            "description": self.description,
            "line_type": self.line_type.value,
            "quantity": str(self.quantity),
            "unit_price": str(self.unit_price),
            "proration_factor": str(self.proration_factor),
            "amount": str(self.amount),
            "payer": self.payer.value,
            "employer_amount": str(self.employer_amount),
            "employee_amount": str(self.employee_amount),
            "taxable": self.taxable,
            "gl_account": self.gl_account,
            "service_month": self.service_month.isoformat(),
        }


@dataclass
class MemberInvoice:
    member_id: int | None
    lines: list[LineItem] = field(default_factory=list)

    @property
    def employer_fee(self) -> Decimal:
        return money(sum((l.employer_amount for l in self.lines), Decimal("0")))

    @property
    def employee_fee(self) -> Decimal:
        return money(sum((l.employee_amount for l in self.lines), Decimal("0")))

    @property
    def total_fee(self) -> Decimal:
        return money(sum((l.amount for l in self.lines), Decimal("0")))


@dataclass
class InvoiceResult:
    client_id: int
    service_month: date
    member_invoices: list[MemberInvoice] = field(default_factory=list)
    # member-count buckets preserved for payments + commissions
    current_member_count: int = 0
    backbilled_member_count: int = 0
    credited_member_count: int = 0

    @property
    def all_lines(self) -> list[LineItem]:
        return [l for mi in self.member_invoices for l in mi.lines]

    @property
    def employer_fee(self) -> Decimal:
        return money(sum((mi.employer_fee for mi in self.member_invoices), Decimal("0")))

    @property
    def employee_fee(self) -> Decimal:
        return money(sum((mi.employee_fee for mi in self.member_invoices), Decimal("0")))

    @property
    def total_fee(self) -> Decimal:
        return money(sum((mi.total_fee for mi in self.member_invoices), Decimal("0")))
