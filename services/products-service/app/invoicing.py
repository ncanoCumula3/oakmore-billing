"""Invoice workflow: generate an itemized invoice from products, persist it, finalize it."""
from __future__ import annotations
from datetime import date
from decimal import Decimal
from typing import Annotated
from fastapi import APIRouter, Header, Depends, Body, HTTPException
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from . import db, models
from .domain import Product as DProduct, Enrollment, MemberCtx
from .enums import PricingModel, Payer, Scope, LineType
from .generator import generate_invoice

router = APIRouter(prefix="/mm/invoices", tags=["invoicing"])


async def sess(x_company_id: Annotated[str, Header()]) -> AsyncSession:
    db.set_tenant(x_company_id)
    async with db.session_factory(x_company_id)() as s:
        yield s

S = Annotated[AsyncSession, Depends(sess)]


def _to_domain(p: models.Product) -> DProduct:
    return DProduct(code=p.code, name=p.name, pricing_model=PricingModel(p.pricing_model),
                    payer=Payer(p.payer), taxable=p.taxable, gl_account=p.gl_account,
                    prorate=p.prorate, sort_order=p.sort_order, employer_split=p.employer_split)


async def _resolve(s: AsyncSession, client_id: int, service_month: date):
    products = (await s.execute(select(models.Product).where(models.Product.active))).scalars().all()
    catalog = {p.code: _to_domain(p) for p in products}
    by_id = {p.id: p for p in products}
    price = lambda r: r.price_override if r.price_override is not None else Decimal("0")
    crows = (await s.execute(select(models.ClientProduct).where(
        models.ClientProduct.client_id == client_id, ~models.ClientProduct.is_invalid))).scalars().all()
    client_enr = [Enrollment(by_id[r.product_id].code, Scope(r.scope), price(r), r.quantity, None,
                             r.effective_date, r.end_date) for r in crows]
    mids = [r[0] for r in (await s.execute(text("""
        SELECT m.id FROM members m JOIN LATERAL (SELECT member_status FROM member_status ms
          WHERE ms.member_id=m.id AND COALESCE(ms.is_invalid,false)=false AND ms.effective_date<=:a
          ORDER BY ms.effective_date DESC, ms.id DESC LIMIT 1) st ON true
        WHERE m.client_id=:c AND st.member_status='ACTIVE'"""), {"c": client_id, "a": service_month})).all()]
    members = [MemberCtx(mid, LineType.CURRENT) for mid in mids]
    mrows = (await s.execute(select(models.MemberProduct).where(
        models.MemberProduct.member_id.in_(mids or [-1]), ~models.MemberProduct.is_invalid))).scalars().all()
    menr: dict[int, list[Enrollment]] = {}
    for r in mrows:
        menr.setdefault(r.member_id, []).append(
            Enrollment(by_id[r.product_id].code, Scope.ALL_MEMBERS, price(r), r.quantity, r.member_id,
                       r.effective_date, r.end_date))
    return catalog, members, client_enr, menr, {p.code: p.id for p in products}


@router.post("/generate")
async def generate(s: S, body: dict = Body(...)):
    cid = int(body["client_id"]); sm = date.fromisoformat(str(body.get("service_month", "2026-07-01")))
    catalog, members, cenr, menr, code2id = await _resolve(s, cid, sm)
    if not catalog:
        raise HTTPException(404, "no products configured")
    inv = generate_invoice(cid, sm, members, catalog, cenr, menr)
    cname = (await s.execute(text("SELECT client_name FROM clients WHERE id=:i"), {"i": cid})).scalar()
    # header
    hid = (await s.execute(text("""INSERT INTO billing.client_invoice
        (client_id,client_name,service_month,status,employer_fee,employee_fee,total_fee,member_count,line_count)
        VALUES(:c,:n,:m,'DRAFT',:ef,:ee,:tf,:mc,:lc) RETURNING id"""),
        {"c": cid, "n": cname, "m": sm, "ef": inv.employer_fee, "ee": inv.employee_fee, "tf": inv.total_fee,
         "mc": len([mi for mi in inv.member_invoices if mi.member_id]), "lc": len(inv.all_lines)})).scalar()
    # lines
    for mi in inv.member_invoices:
        for l in mi.lines:
            await s.execute(text("""INSERT INTO billing.invoice_line_items
              (billing_invoice_id,client_invoice_id,member_id,product_id,product_code,description,line_type,
               quantity,unit_price,proration_factor,amount,payer,employer_amount,employee_amount,taxable,gl_account,service_month)
              VALUES(:bi,0,:mid,:pid,:pc,:d,:lt,:q,:up,:pf,:amt,:pay,:er,:ee,:tax,:gl,:sm)"""),
              {"bi": hid, "mid": l.member_id, "pid": code2id.get(l.product_code, 0), "pc": l.product_code,
               "d": l.description, "lt": l.line_type.value, "q": l.quantity, "up": l.unit_price,
               "pf": l.proration_factor, "amt": l.amount, "pay": l.payer.value, "er": l.employer_amount,
               "ee": l.employee_amount, "tax": l.taxable, "gl": l.gl_account, "sm": l.service_month})
    await s.commit()
    return {"id": hid, "client_name": cname, "total_fee": str(inv.total_fee),
            "member_count": len([mi for mi in inv.member_invoices if mi.member_id]), "line_count": len(inv.all_lines), "status": "DRAFT"}


@router.get("")
async def list_invoices(s: S):
    r = await s.execute(text("""SELECT id,client_id,client_name,service_month,status,total_fee,member_count,line_count,created_at,finalized_at
        FROM billing.client_invoice ORDER BY created_at DESC LIMIT 200"""))
    return [dict(m) for m in r.mappings().all()]


@router.get("/{iid}")
async def get_invoice(iid: int, s: S):
    h = (await s.execute(text("SELECT * FROM billing.client_invoice WHERE id=:i"), {"i": iid})).mappings().first()
    if not h: raise HTTPException(404, "not found")
    lines = (await s.execute(text("""SELECT member_id,product_code,description,quantity,unit_price,amount,payer,employer_amount,employee_amount
        FROM billing.invoice_line_items WHERE billing_invoice_id=:i ORDER BY member_id, product_code LIMIT 5000"""), {"i": iid})).mappings().all()
    return {"invoice": dict(h), "lines": [dict(x) for x in lines]}


@router.post("/{iid}/finalize")
async def finalize(iid: int, s: S):
    await s.execute(text("UPDATE billing.client_invoice SET status='FINAL', finalized_at=now() WHERE id=:i"), {"i": iid})
    await s.commit()
    return {"id": iid, "status": "FINAL"}
