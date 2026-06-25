"""Data enrichment and KPI calculations."""

from datetime import datetime, timedelta
from typing import Optional

import numpy as np
import pandas as pd

from utils.config import NOTICE_PERIOD_DAYS
from utils.risk_engine import compute_risk_scores


def _today() -> pd.Timestamp:
    return pd.Timestamp(datetime.now().date())


def enrich_contracts(
    contracts: pd.DataFrame,
    pos: pd.DataFrame,
    payments: pd.DataFrame,
    sla: pd.DataFrame,
    approval_threshold: float,
) -> pd.DataFrame:
    """Enrich contract master with computed fields."""
    if contracts.empty:
        return contracts

    df = contracts.copy()
    today = _today()

    df["Days to Expiry"] = (df["End Date"] - today).dt.days
    df["Expiry Status"] = df["Days to Expiry"].apply(_expiry_status)
    df["Is Active"] = (df["Start Date"] <= today) & (df["End Date"] >= today)
    df["Is Expired"] = df["End Date"] < today
    df["Auto Renew Flag"] = df.get("Auto Renew", pd.Series(dtype=str)).astype(str).str.upper().str.strip().isin(["Y", "YES", "TRUE", "1"])

    # PO and payment totals
    if not pos.empty and "Contract ID" in pos.columns:
        po_totals = pos.groupby("Contract ID")["PO Amount"].sum().reset_index(name="PO Total")
        df = df.merge(po_totals, on="Contract ID", how="left")
    else:
        df["PO Total"] = 0.0

    if not payments.empty and "Contract ID" in payments.columns:
        pay_totals = payments.groupby("Contract ID")["Payment Amount"].sum().reset_index(name="Payments Total")
        df = df.merge(pay_totals, on="Contract ID", how="left")
    else:
        df["Payments Total"] = 0.0

    df["PO Total"] = df["PO Total"].fillna(0)
    df["Payments Total"] = df["Payments Total"].fillna(0)

    df["PO Variance"] = df["PO Total"] - df["Contract Value"]
    df["Payment Variance"] = df["Payments Total"] - df["Contract Value"]
    df["PO Overrun %"] = np.where(
        df["Contract Value"] > 0,
        (df["PO Variance"] / df["Contract Value"] * 100).round(1),
        0,
    )
    df["Payment Overrun %"] = np.where(
        df["Contract Value"] > 0,
        (df["Payment Variance"] / df["Contract Value"] * 100).round(1),
        0,
    )
    df["Overrun Status"] = df.apply(_overrun_status, axis=1)

    # SLA
    if "SLA Actual %" in df.columns and "SLA Target %" in df.columns:
        df["SLA Compliant"] = df["SLA Actual %"] >= df["SLA Target %"]
        df["SLA Breach"] = ~df["SLA Compliant"].fillna(True)
    else:
        df["SLA Breach"] = False

    if not sla.empty:
        sla_failures = sla[sla["SLA Actual"] < sla["SLA Target"]].groupby("Contract ID").size()
        df["SLA Failure Count"] = df["Contract ID"].map(sla_failures).fillna(0).astype(int)
        df["Repeated SLA Failures"] = df["SLA Failure Count"] >= 2
    else:
        df["SLA Failure Count"] = 0
        df["Repeated SLA Failures"] = False

    # Signatures
    sig = df.get("Signature Status", pd.Series(dtype=str)).astype(str).str.lower()
    df["Signature Missing"] = sig.isin(["unsigned", "missing", "pending", "no", ""]) | sig.isna()
    df["Signature Compliant"] = ~df["Signature Missing"]

    # Approvals
    df["Above Threshold"] = df["Contract Value"] >= approval_threshold
    legal = df.get("Legal Approval", pd.Series(dtype=str)).astype(str).str.lower()
    board = df.get("Board Approval", pd.Series(dtype=str)).astype(str).str.lower()
    df["Legal Approved"] = legal.isin(["yes", "y", "approved", "complete"])
    df["Board Approved"] = board.isin(["yes", "y", "approved", "complete"])
    df["Missing Legal Approval"] = df["Above Threshold"] & ~df["Legal Approved"]
    df["Missing Board Approval"] = df["Above Threshold"] & ~df["Board Approved"]
    df["Missing Approvals"] = df["Missing Legal Approval"] | df["Missing Board Approval"]

    # Auto-renewal dates
    df["Renewal Date"] = df["End Date"]
    df["Notice Deadline"] = df["End Date"] - pd.Timedelta(days=NOTICE_PERIOD_DAYS)
    df["Notice Alert"] = df["Auto Renew Flag"] & (df["Notice Deadline"] <= today + pd.Timedelta(days=NOTICE_PERIOD_DAYS))

    # Risk scoring
    df = compute_risk_scores(df)

    return df


def _expiry_status(days: float) -> str:
    if pd.isna(days):
        return "Unknown"
    if days < 0:
        return "Expired"
    if days <= 30:
        return "Expiring in 30 Days"
    if days <= 60:
        return "Expiring in 60 Days"
    if days <= 90:
        return "Expiring in 90 Days"
    return "Active"


def _overrun_status(row: pd.Series) -> str:
    if row.get("Payments Total", 0) > row.get("Contract Value", 0):
        return "Critical"
    if row.get("PO Total", 0) > row.get("Contract Value", 0):
        return "Warning"
    return "Compliant"


def compute_kpis(df: pd.DataFrame) -> dict:
    """Compute executive dashboard KPIs."""
    if df.empty:
        return {k: 0 for k in [
            "total", "active", "expiring_30", "expiring_90", "auto_renew",
            "high_risk", "sla_breaches", "overruns", "missing_approvals",
        ]}

    today = _today()
    return {
        "total": len(df),
        "active": int(df["Is Active"].sum()) if "Is Active" in df.columns else 0,
        "expiring_30": int((df["Days to Expiry"].between(0, 30)).sum()) if "Days to Expiry" in df.columns else 0,
        "expiring_90": int((df["Days to Expiry"].between(0, 90)).sum()) if "Days to Expiry" in df.columns else 0,
        "auto_renew": int(df["Auto Renew Flag"].sum()) if "Auto Renew Flag" in df.columns else 0,
        "high_risk": int(df["Risk Category"].isin(["High", "Critical"]).sum()) if "Risk Category" in df.columns else 0,
        "sla_breaches": int(df["SLA Breach"].sum()) if "SLA Breach" in df.columns else 0,
        "overruns": int((df["Overrun Status"] != "Compliant").sum()) if "Overrun Status" in df.columns else 0,
        "missing_approvals": int(df["Missing Approvals"].sum()) if "Missing Approvals" in df.columns else 0,
    }


def get_contract_status_distribution(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "Expiry Status" not in df.columns:
        return pd.DataFrame(columns=["Status", "Count"])
    return df["Expiry Status"].value_counts().reset_index().rename(columns={"index": "Status", "Expiry Status": "Count"})
