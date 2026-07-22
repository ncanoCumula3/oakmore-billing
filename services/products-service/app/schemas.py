"""Pydantic v2 DTOs (shared contracts). Would live in `oakmore-contracts`."""
from __future__ import annotations
from datetime import date
from decimal import Decimal
from pydantic import BaseModel, Field

from .enums import PricingModel, Payer, Scope, LineType, Category, BillingFrequency


class ProductIn(BaseModel):
    code: str
    name: str
    category: Category = Category.CUSTOM
    pricing_model: PricingModel = PricingModel.FLAT
    payer: Payer = Payer.EMPLOYER
    taxable: bool = False
    gl_account: str | None = None
    billing_frequency: BillingFrequency = BillingFrequency.MONTHLY
    prorate: bool = False
    employer_split: Decimal = Decimal("0")
    sort_order: int = 100


class ProductOut(ProductIn):
    id: int
    active: bool = True


class PriceIn(BaseModel):
    amount: Decimal
    employer_split: Decimal = Decimal("0")
    effective_date: date


class EnrollmentIn(BaseModel):
    product_code: str
    scope: Scope = Scope.ALL_MEMBERS
    quantity: Decimal = Decimal("1")
    price_override: Decimal | None = None
    member_id: int | None = None
    effective_date: date | None = None
    end_date: date | None = None


class PreviewRequest(BaseModel):
    client_id: int
    service_month: date


class LineItemOut(BaseModel):
    member_id: int | None
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


class MemberInvoiceOut(BaseModel):
    member_id: int | None
    employer_fee: Decimal
    employee_fee: Decimal
    total_fee: Decimal
    lines: list[LineItemOut]


class InvoicePreviewOut(BaseModel):
    client_id: int
    service_month: date
    employer_fee: Decimal
    employee_fee: Decimal
    total_fee: Decimal
    current_member_count: int
    backbilled_member_count: int
    credited_member_count: int
    members: list[MemberInvoiceOut]
