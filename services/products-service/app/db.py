"""
Tenant routing: DB-per-tenant. Each request carries X-Company-Id; we resolve that tenant's
DSN and hand back an async session bound to it. Engines are cached per tenant DSN.
"""
from __future__ import annotations
import os
from contextvars import ContextVar
from functools import lru_cache

from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker, AsyncSession

_tenant: ContextVar[str] = ContextVar("tenant", default="")

# Tenant id -> name, matching the existing convention (extend/replace with the Tenant service).
TENANT_NAMES = {"1": "oakmorelabs", "2": "quicksoft", "3": "attentive", "4": "incent",
                "5": "proactivehealth_solutions", "6": "attentive_demo_hub", "8": "next_level"}


def set_tenant(company_id: str) -> None:
    _tenant.set(company_id)


def current_tenant() -> str:
    t = _tenant.get()
    if not t:
        raise RuntimeError("no tenant in context (missing X-Company-Id)")
    return t


def tenant_dsn(company_id: str) -> str:
    """Resolve the tenant's Postgres DSN from env (TENANT_<NAME>_DATABASE_URL)."""
    name = TENANT_NAMES.get(company_id, company_id).upper()
    dsn = os.environ.get(f"TENANT_{name}_DATABASE_URL") or os.environ.get("DATABASE_URL")
    if not dsn:
        raise RuntimeError(f"no DSN for tenant {company_id} (set TENANT_{name}_DATABASE_URL)")
    # normalise to asyncpg driver
    return dsn.replace("postgresql://", "postgresql+asyncpg://").replace("postgres://", "postgresql+asyncpg://")


@lru_cache(maxsize=64)
def _engine(dsn: str) -> AsyncEngine:
    return create_async_engine(dsn, pool_size=5, max_overflow=5, pool_pre_ping=True)


def session_factory(company_id: str) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(_engine(tenant_dsn(company_id)), expire_on_commit=False)
