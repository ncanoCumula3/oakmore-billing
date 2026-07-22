"""
Member Manager API over the real tenant tables (clients, members, brokers, invoices,
payments, commissions, fees, contacts). Read + key writes. Raw SQL matched to the real columns.
"""
from __future__ import annotations
from datetime import date
from typing import Annotated, Any
from fastapi import APIRouter, Header, Depends, Body
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from .db import set_tenant, session_factory

router = APIRouter(prefix="/mm", tags=["member-manager"])


async def sess(x_company_id: Annotated[str, Header()]) -> AsyncSession:
    set_tenant(x_company_id)
    async with session_factory(x_company_id)() as s:
        yield s

S = Annotated[AsyncSession, Depends(sess)]


async def rows(s: AsyncSession, sql: str, **p) -> list[dict]:
    r = await s.execute(text(sql), p)
    return [dict(m) for m in r.mappings().all()]


async def one(s: AsyncSession, sql: str, **p) -> dict | None:
    r = await s.execute(text(sql), p)
    m = r.mappings().first()
    return dict(m) if m else None


# ---------------- Dashboard ----------------
@router.get("/summary")
async def summary(s: S):
    return await one(s, """
      SELECT (SELECT count(*) FROM clients) clients,
             (SELECT count(*) FROM members) members,
             (SELECT count(*) FROM brokers) brokers,
             (SELECT count(*) FROM agencies) agencies,
             (SELECT count(*) FROM invoice_processes) invoice_processes,
             (SELECT count(*) FROM client_invoices) client_invoices,
             (SELECT count(*) FROM client_payments) payments,
             (SELECT count(*) FROM commission_runs) commission_runs""")


# ---------------- Clients ----------------
@router.get("/clients")
async def clients(s: S, q: str = "", limit: int = 50, offset: int = 0):
    return await rows(s, """
      SELECT id, client_name, client_status, lives, billing_freq, account_manager, broker,
             city, state FROM clients
      WHERE (:q='' OR client_name ILIKE '%'||:q||'%')
      ORDER BY client_name LIMIT :lim OFFSET :off""", q=q, lim=limit, off=offset)


@router.get("/clients/{cid}")
async def client(cid: int, s: S):
    c = await one(s, "SELECT * FROM clients WHERE id=:i", i=cid)
    fee = await one(s, """SELECT employer_fee, employee_fee, premium, effective_date FROM client_fee
                          WHERE client_id=:i AND COALESCE(is_invalid,false)=false
                          ORDER BY effective_date DESC, id DESC LIMIT 1""", i=cid)
    contacts = await rows(s, "SELECT first_name,last_name,email,phone,is_invoice_contact,is_payroll_contact,is_primary_contact FROM client_contacts WHERE client_id=:i", i=cid)
    brokers = await rows(s, """SELECT b.id, b.broker_name, ctb.commission_rate_pepm, ctb.is_primary, ctb.effective_date
                               FROM clients_to_brokers ctb JOIN brokers b ON b.id=ctb.broker_id
                               WHERE ctb.client_id=:i AND COALESCE(ctb.is_invalid,false)=false""", i=cid)
    mcount = await one(s, "SELECT count(*) n FROM members WHERE client_id=:i", i=cid)
    return {"client": c, "fee": fee, "contacts": contacts, "brokers": brokers, "member_count": mcount["n"] if mcount else 0}


# ---------------- Members ----------------
@router.get("/clients/{cid}/members")
async def members(cid: int, s: S, q: str = "", asof: date | None = None):
    asof = asof or date.today()
    return await rows(s, """
      SELECT m.id, m.first_name, m.last_name, m.ssn, m.dependent_type, m.email, m.client_employee_id,
             st.member_status status, m.pcm_pre_tax, m.pcm_after_tax, m.admin_fee_after_tax, m.simrp_fee_after_tax
      FROM members m
      JOIN LATERAL (SELECT member_status FROM member_status ms WHERE ms.member_id=m.id
                    AND COALESCE(ms.is_invalid,false)=false AND ms.effective_date<=:asof
                    ORDER BY ms.effective_date DESC, ms.id DESC LIMIT 1) st ON true
      WHERE m.client_id=:i AND (:q='' OR (m.first_name||' '||m.last_name) ILIKE '%'||:q||'%')
      ORDER BY m.last_name, m.first_name LIMIT 1000""", i=cid, q=q, asof=asof)


@router.get("/members/{mid}")
async def member(mid: int, s: S):
    m = await one(s, "SELECT * FROM members WHERE id=:i", i=mid)
    hist = await rows(s, """SELECT member_status, effective_date, comment, modified_by, is_invalid
                            FROM member_status WHERE member_id=:i ORDER BY effective_date DESC, id DESC""", i=mid)
    deps = await rows(s, "SELECT id, first_name, last_name, dependent_type FROM members WHERE dependent_of=:i", i=mid)
    return {"member": m, "status_history": hist, "dependents": deps}


@router.patch("/members/{mid}")
async def update_member(mid: int, s: S, body: dict = Body(...)):
    allowed = {"first_name","last_name","email","phone_num","address_line1","city","state","zip_code",
               "client_dept","client_employee_id","admin_fee_after_tax","pcm_pre_tax","pcm_after_tax","simrp_fee_after_tax"}
    sets = {k: v for k, v in body.items() if k in allowed}
    if not sets:
        return {"updated": 0}
    frag = ", ".join(f"{k}=:{k}" for k in sets)
    await s.execute(text(f"UPDATE members SET {frag} WHERE id=:i"), {**sets, "i": mid})
    await s.commit()
    return {"updated": 1, "fields": list(sets)}


@router.post("/members/{mid}/status")
async def add_status(mid: int, s: S, body: dict = Body(...)):
    await s.execute(text("""INSERT INTO member_status(member_id,member_status,effective_date,comment,modified_by,modified_date,is_invalid)
        VALUES(:m,:st,:eff,:cm,:by,now(),false)"""),
        {"m": mid, "st": body["member_status"], "eff": body.get("effective_date", date.today()),
         "cm": body.get("comment", ""), "by": body.get("modified_by", "oakmore-ui")})
    await s.commit()
    return {"ok": True}


# ---------------- Brokers / Agencies ----------------
@router.get("/brokers")
async def brokers(s: S, q: str = "", limit: int = 100):
    return await rows(s, """SELECT b.id, b.broker_name, b.first_name, b.last_name, b.email, a.agency_name
      FROM brokers b LEFT JOIN agencies a ON a.id=b.agency_id
      WHERE (:q='' OR b.broker_name ILIKE '%'||:q||'%') ORDER BY b.broker_name LIMIT :lim""", q=q, lim=limit)


@router.get("/brokers/{bid}")
async def broker(bid: int, s: S):
    b = await one(s, "SELECT * FROM brokers WHERE id=:i", i=bid)
    clients = await rows(s, """SELECT c.id, c.client_name, ctb.commission_rate_pepm, ctb.is_primary
      FROM clients_to_brokers ctb JOIN clients c ON c.id=ctb.client_id
      WHERE ctb.broker_id=:i AND COALESCE(ctb.is_invalid,false)=false ORDER BY c.client_name""", i=bid)
    return {"broker": b, "clients": clients}


@router.get("/agencies")
async def agencies(s: S):
    return await rows(s, """SELECT a.id, a.agency_name, a.head_broker_id, b.broker_name head_broker,
      (SELECT count(*) FROM brokers WHERE agency_id=a.id) brokers
      FROM agencies a LEFT JOIN brokers b ON b.id=a.head_broker_id ORDER BY a.agency_name""")


@router.get("/account-managers")
async def account_managers(s: S):
    return await rows(s, "SELECT id, first_name, last_name, email FROM account_managers ORDER BY last_name")


# ---------------- Invoices ----------------
@router.get("/invoice-processes")
async def invoice_processes(s: S):
    return await rows(s, """SELECT ip.id, ip.process_name, ip.invoice_date, ip.invoicing_process_status status,
      (SELECT count(*) FROM client_invoices ci WHERE ci.invoice_process_id=ip.id) client_invoices
      FROM invoice_processes ip ORDER BY ip.invoice_date DESC NULLS LAST, ip.id DESC""")


@router.get("/invoice-processes/{pid}/client-invoices")
async def process_invoices(pid: int, s: S):
    return await rows(s, """SELECT ci.id, c.client_name, ci.client_invoice_status status, ci.invoice_date,
      ci.payment_method, ci.final_approval_date,
      (SELECT count(*) FROM invoices_final f WHERE f.client_invoice_id=ci.id) lines,
      (SELECT coalesce(sum(total_fee),0) FROM invoices_final f WHERE f.client_invoice_id=ci.id) total
      FROM client_invoices ci LEFT JOIN clients c ON c.id=ci.client_id
      WHERE ci.invoice_process_id=:i ORDER BY c.client_name""", i=pid)


@router.get("/client-invoices/{ciid}/lines")
async def invoice_lines(ciid: int, s: S):
    return await rows(s, """SELECT first_name, last_name, client_employee_id, service_month,
      employer_fee, employee_fee, total_fee, comment FROM invoices_final
      WHERE client_invoice_id=:i ORDER BY last_name, first_name LIMIT 2000""", i=ciid)


# ---------------- Payments ----------------
@router.get("/client-payments")
async def payments(s: S, client_id: int | None = None, limit: int = 100):
    if client_id:
        return await rows(s, """SELECT p.*, c.client_name FROM client_payments p LEFT JOIN clients c ON c.id=p.client_id
          WHERE p.client_id=:i ORDER BY p.payment_initiated_date DESC NULLS LAST LIMIT :lim""", i=client_id, lim=limit)
    return await rows(s, """SELECT p.id, c.client_name, p.payment_method, p.payment_status, p.total_payment_amount,
      p.balance_amount, p.payment_initiated_date, p.payment_cleared_date
      FROM client_payments p LEFT JOIN clients c ON c.id=p.client_id
      ORDER BY p.payment_initiated_date DESC NULLS LAST LIMIT :lim""", lim=limit)


# ---------------- Commissions ----------------
@router.get("/commission-runs")
async def commission_runs(s: S):
    return await rows(s, """SELECT id, run_name, period_start_date, period_end_date, run_status,
      (SELECT count(*) FROM commission_lines l WHERE l.commission_run_id=commission_runs.id) lines,
      (SELECT coalesce(sum(commission_amount),0) FROM commission_lines l WHERE l.commission_run_id=commission_runs.id) total
      FROM commission_runs ORDER BY period_end_date DESC NULLS LAST, id DESC""")


@router.get("/commission-rates")
async def commission_rates(s: S, limit: int = 200):
    return await rows(s, """SELECT c.client_name, b.broker_name, ctb.commission_rate_pepm, ctb.is_primary, ctb.effective_date
      FROM clients_to_brokers ctb JOIN clients c ON c.id=ctb.client_id JOIN brokers b ON b.id=ctb.broker_id
      WHERE COALESCE(ctb.is_invalid,false)=false ORDER BY c.client_name LIMIT :lim""", lim=limit)
