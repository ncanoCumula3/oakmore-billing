"""
Products service — FastAPI. Products CRUD + invoice-line preview.
Auth is delegated to the reused core-auth service (validate the bearer token there); omitted here
for brevity. Tenant comes from X-Company-Id.
"""
from __future__ import annotations
from datetime import date
from decimal import Decimal
from typing import Annotated

from fastapi import FastAPI, Header, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from . import db, models
from .schemas import ProductIn, ProductOut, PreviewRequest, InvoicePreviewOut, MemberInvoiceOut, LineItemOut
from .domain import Product as DProduct, Enrollment, MemberCtx
from .enums import PricingModel, Payer, Scope, LineType
from .generator import generate_invoice

from . import accounts, ui, mm

app = FastAPI(title="Oakmore Billing — Member Manager", version="0.2.0")
app.include_router(accounts.router)
app.include_router(mm.router)
app.include_router(ui.router)

# permissive CORS for the Reflex UI (tighten at the gateway later)
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


async def get_session(x_company_id: Annotated[str, Header()]) -> AsyncSession:
    db.set_tenant(x_company_id)
    async with db.session_factory(x_company_id)() as s:
        yield s


Session = Annotated[AsyncSession, Depends(get_session)]


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/products", response_model=list[ProductOut])
async def list_products(s: Session) -> list[models.Product]:
    rows = (await s.execute(select(models.Product).where(models.Product.active))).scalars().all()
    return list(rows)


@app.post("/products", response_model=ProductOut, status_code=201)
async def create_product(body: ProductIn, s: Session) -> models.Product:
    p = models.Product(**body.model_dump())
    s.add(p)
    await s.commit()
    await s.refresh(p)
    return p


def _to_domain(p: models.Product) -> DProduct:
    return DProduct(code=p.code, name=p.name, pricing_model=PricingModel(p.pricing_model),
                    payer=Payer(p.payer), taxable=p.taxable, gl_account=p.gl_account,
                    prorate=p.prorate, sort_order=p.sort_order, employer_split=p.employer_split)


async def _resolve_inputs(s: AsyncSession, client_id: int, service_month: date):
    """Load catalog + enrollments + active members from the tenant DB (Accounts read model)."""
    products = (await s.execute(select(models.Product).where(models.Product.active))).scalars().all()
    catalog = {p.code: _to_domain(p) for p in products}
    by_id = {p.id: p for p in products}

    def price(row) -> Decimal:
        return row.price_override if row.price_override is not None else Decimal("0")

    client_rows = (await s.execute(
        select(models.ClientProduct).where(models.ClientProduct.client_id == client_id,
                                            ~models.ClientProduct.is_invalid))).scalars().all()
    client_enr = [Enrollment(by_id[r.product_id].code, Scope(r.scope), price(r), r.quantity,
                             None, r.effective_date, r.end_date) for r in client_rows]

    # active members for the period — resolved via the Accounts read model (members + latest status).
    sql = """
      SELECT m.id FROM members m
      JOIN LATERAL (SELECT member_status, effective_date FROM member_status ms
                    WHERE ms.member_id=m.id AND COALESCE(ms.is_invalid,false)=false
                      AND ms.effective_date <= :asof
                    ORDER BY ms.effective_date DESC, ms.id DESC LIMIT 1) st ON true
      WHERE m.client_id=:cid AND st.member_status='ACTIVE'
    """
    from sqlalchemy import text
    mids = [r[0] for r in (await s.execute(text(sql), {"cid": client_id, "asof": service_month})).all()]
    members = [MemberCtx(member_id=mid, line_type=LineType.CURRENT) for mid in mids]

    mem_rows = (await s.execute(
        select(models.MemberProduct).where(models.MemberProduct.member_id.in_(mids or [-1]),
                                            ~models.MemberProduct.is_invalid))).scalars().all()
    member_enr: dict[int, list[Enrollment]] = {}
    for r in mem_rows:
        member_enr.setdefault(r.member_id, []).append(
            Enrollment(by_id[r.product_id].code, Scope.ALL_MEMBERS, price(r), r.quantity,
                       r.member_id, r.effective_date, r.end_date))
    return catalog, members, client_enr, member_enr


@app.post("/invoices/preview-lines", response_model=InvoicePreviewOut)
async def preview_lines(body: PreviewRequest, s: Session) -> InvoicePreviewOut:
    catalog, members, client_enr, member_enr = await _resolve_inputs(s, body.client_id, body.service_month)
    if not catalog:
        raise HTTPException(404, "no products configured for tenant")
    inv = generate_invoice(body.client_id, body.service_month, members, catalog, client_enr, member_enr)
    return InvoicePreviewOut(
        client_id=inv.client_id, service_month=inv.service_month,
        employer_fee=inv.employer_fee, employee_fee=inv.employee_fee, total_fee=inv.total_fee,
        current_member_count=inv.current_member_count,
        backbilled_member_count=inv.backbilled_member_count,
        credited_member_count=inv.credited_member_count,
        members=[MemberInvoiceOut(
            member_id=mi.member_id, employer_fee=mi.employer_fee, employee_fee=mi.employee_fee,
            total_fee=mi.total_fee,
            lines=[LineItemOut(**l.__dict__) for l in mi.lines],
        ) for mi in inv.member_invoices],
    )
