"""Accounts read endpoints (clients + members) for the MVP core API — read the tenant DB."""
from __future__ import annotations
from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from .db import set_tenant, session_factory
from fastapi import Header
from typing import Annotated

router = APIRouter(tags=["accounts"])


async def get_session(x_company_id: Annotated[str, Header()]) -> AsyncSession:
    set_tenant(x_company_id)
    async with session_factory(x_company_id)() as s:
        yield s


@router.get("/clients")
async def clients(s: Annotated[AsyncSession, Depends(get_session)], q: str = "", limit: int = 50):
    sql = """SELECT id, client_name, client_status FROM clients
             WHERE (%(q)s = '' OR client_name ILIKE '%%'||%(q)s||'%%')
             ORDER BY client_name LIMIT %(lim)s"""
    rows = (await s.execute(text(sql.replace('%(q)s', ':q').replace('%(lim)s', ':lim')),
                            {"q": q, "lim": limit})).all()
    return [{"id": r[0], "client_name": r[1], "client_status": r[2]} for r in rows]


@router.get("/clients/{client_id}/members")
async def members(client_id: int, s: Annotated[AsyncSession, Depends(get_session)],
                  asof: date | None = None):
    asof = asof or date.today()
    sql = """
      SELECT m.id, m.first_name, m.last_name, m.ssn, m.dependent_type, st.member_status,
             m.pcm_pre_tax, m.pcm_after_tax, m.admin_fee_after_tax, m.simrp_fee_after_tax
      FROM members m
      JOIN LATERAL (SELECT member_status FROM member_status ms
                    WHERE ms.member_id=m.id AND COALESCE(ms.is_invalid,false)=false
                      AND ms.effective_date <= :asof
                    ORDER BY ms.effective_date DESC, ms.id DESC LIMIT 1) st ON true
      WHERE m.client_id=:cid ORDER BY m.last_name, m.first_name LIMIT 500
    """
    rows = (await s.execute(text(sql), {"cid": client_id, "asof": asof})).all()
    return [{"id": r[0], "first_name": r[1], "last_name": r[2], "ssn": r[3],
             "dependent_type": r[4], "status": r[5],
             "deductions": {"pcm_pre_tax": str(r[6] or 0), "pcm_after_tax": str(r[7] or 0),
                            "admin_fee_after_tax": str(r[8] or 0), "simrp_fee_after_tax": str(r[9] or 0)}}
            for r in rows]
