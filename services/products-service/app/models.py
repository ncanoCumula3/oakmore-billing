"""SQLAlchemy 2.0 typed models — billing schema, one DB per tenant."""
from __future__ import annotations
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import String, Integer, Numeric, Boolean, Date, DateTime, ForeignKey, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

SCHEMA = "billing"


class Base(DeclarativeBase):
    metadata = __import__("sqlalchemy").MetaData(schema=SCHEMA)


class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(String, default=None)
    category: Mapped[str] = mapped_column(String, default="CUSTOM")
    pricing_model: Mapped[str] = mapped_column(String, default="FLAT")
    payer: Mapped[str] = mapped_column(String, default="EMPLOYER")
    taxable: Mapped[bool] = mapped_column(Boolean, default=False)
    gl_account: Mapped[str | None] = mapped_column(String, default=None)
    billing_frequency: Mapped[str] = mapped_column(String, default="MONTHLY")
    prorate: Mapped[bool] = mapped_column(Boolean, default=False)
    employer_split: Mapped[Decimal] = mapped_column(Numeric(6, 4), default=Decimal("0"))
    sort_order: Mapped[int] = mapped_column(Integer, default=100)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"))
    prices: Mapped[list["ProductPrice"]] = relationship(back_populates="product")


class ProductPrice(Base):
    __tablename__ = "product_prices"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey(f"{SCHEMA}.products.id"), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    percentage: Mapped[Decimal | None] = mapped_column(Numeric(6, 4), default=None)
    employer_split: Mapped[Decimal] = mapped_column(Numeric(6, 4), default=Decimal("0"))
    effective_date: Mapped[date] = mapped_column(Date)
    is_invalid: Mapped[bool] = mapped_column(Boolean, default=False)
    product: Mapped[Product] = relationship(back_populates="prices")


class ClientProduct(Base):
    __tablename__ = "client_products"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    client_id: Mapped[int] = mapped_column(Integer, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey(f"{SCHEMA}.products.id"))
    scope: Mapped[str] = mapped_column(String, default="ALL_MEMBERS")   # ALL_MEMBERS | CLIENT_FLAT
    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("1"))
    price_override: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), default=None)
    payer_override: Mapped[str | None] = mapped_column(String, default=None)
    effective_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date, default=None)
    is_invalid: Mapped[bool] = mapped_column(Boolean, default=False)


class MemberProduct(Base):
    __tablename__ = "member_products"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    member_id: Mapped[int] = mapped_column(Integer, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey(f"{SCHEMA}.products.id"))
    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("1"))
    price_override: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), default=None)
    payer_override: Mapped[str | None] = mapped_column(String, default=None)
    effective_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date, default=None)
    is_invalid: Mapped[bool] = mapped_column(Boolean, default=False)
    modified_by: Mapped[str | None] = mapped_column(String, default=None)
    modified_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"))


class InvoiceLineItem(Base):
    __tablename__ = "invoice_line_items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    client_invoice_id: Mapped[int] = mapped_column(Integer, index=True)
    invoices_final_id: Mapped[int | None] = mapped_column(Integer, default=None, index=True)
    member_id: Mapped[int | None] = mapped_column(Integer, default=None, index=True)  # NULL = CLIENT_FLAT
    product_id: Mapped[int] = mapped_column(Integer)
    product_code: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(String, default=None)
    line_type: Mapped[str] = mapped_column(String, default="CURRENT")
    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("1"))
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    proration_factor: Mapped[Decimal] = mapped_column(Numeric(9, 6), default=Decimal("1"))
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    payer: Mapped[str] = mapped_column(String)
    employer_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0"))
    employee_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0"))
    taxable: Mapped[bool] = mapped_column(Boolean, default=False)
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0"))
    gl_account: Mapped[str | None] = mapped_column(String, default=None)
    service_month: Mapped[date] = mapped_column(Date)
