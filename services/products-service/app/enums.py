"""Enums for the Products / billing domain. Reserved slots kept for deferred pricing models."""
from __future__ import annotations
from enum import Enum


class PricingModel(str, Enum):
    FLAT = "FLAT"                # built now
    PER_MEMBER = "PER_MEMBER"    # deferred
    PER_DEPENDENT = "PER_DEPENDENT"  # deferred
    PERCENTAGE = "PERCENTAGE"    # parked (base undefined)
    TIERED = "TIERED"            # deferred


class Payer(str, Enum):
    EMPLOYER = "EMPLOYER"
    EMPLOYEE = "EMPLOYEE"
    SPLIT = "SPLIT"
    NONE = "NONE"


class Scope(str, Enum):
    ALL_MEMBERS = "ALL_MEMBERS"   # one line per active member
    CLIENT_FLAT = "CLIENT_FLAT"   # one line on the client invoice, member_id NULL


class LineType(str, Enum):
    CURRENT = "CURRENT"
    BACKBILLED = "BACKBILLED"
    CREDIT = "CREDIT"
    ADJUSTMENT = "ADJUSTMENT"


class Category(str, Enum):
    MEDICAL = "MEDICAL"
    ADMIN_FEE = "ADMIN_FEE"
    PCM = "PCM"
    SIMRP = "SIMRP"
    SUPP = "SUPP"
    CUSTOM = "CUSTOM"


class BillingFrequency(str, Enum):
    MONTHLY = "MONTHLY"
    ONE_TIME = "ONE_TIME"
    ANNUAL = "ANNUAL"
