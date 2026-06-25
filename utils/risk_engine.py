"""Automated contract risk scoring engine."""

import pandas as pd

from utils.config import RISK_WEIGHTS


def compute_risk_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Apply weighted risk factors and categorize contracts."""
    if df.empty:
        return df

    result = df.copy()
    scores = pd.Series(0, index=result.index, dtype=float)

    if "Signature Missing" in result.columns:
        scores += result["Signature Missing"].astype(bool) * RISK_WEIGHTS["signature_missing"]

    if "Is Expired" in result.columns:
        scores += result["Is Expired"].astype(bool) * RISK_WEIGHTS["expired"]

    if "Auto Renew Flag" in result.columns:
        scores += result["Auto Renew Flag"].astype(bool) * RISK_WEIGHTS["auto_renew"]

    if "SLA Breach" in result.columns:
        scores += result["SLA Breach"].astype(bool) * RISK_WEIGHTS["sla_breach"]

    if "Overrun Status" in result.columns:
        scores += (result["Overrun Status"] == "Critical").astype(int) * RISK_WEIGHTS["overrun"]
        scores += (result["Overrun Status"] == "Warning").astype(int) * (RISK_WEIGHTS["overrun"] * 0.5)

    if "Missing Board Approval" in result.columns:
        scores += result["Missing Board Approval"].astype(bool) * RISK_WEIGHTS["missing_board_approval"]

    result["Risk Score"] = scores.clip(0, 100).round(0).astype(int)
    result["Risk Category"] = result["Risk Score"].apply(_categorize_risk)
    return result


def _categorize_risk(score: int) -> str:
    if score >= 75:
        return "Critical"
    if score >= 50:
        return "High"
    if score >= 25:
        return "Medium"
    return "Low"


def get_risk_heatmap_data(df: pd.DataFrame) -> pd.DataFrame:
    """Pivot risk factors by vendor for heatmap."""
    if df.empty:
        return pd.DataFrame()

    factors = pd.DataFrame({
        "Vendor": df["Vendor"],
        "Signature": df.get("Signature Missing", False).astype(int) * RISK_WEIGHTS["signature_missing"],
        "Expired": df.get("Is Expired", False).astype(int) * RISK_WEIGHTS["expired"],
        "Auto-Renew": df.get("Auto Renew Flag", False).astype(int) * RISK_WEIGHTS["auto_renew"],
        "SLA": df.get("SLA Breach", False).astype(int) * RISK_WEIGHTS["sla_breach"],
        "Overrun": (df.get("Overrun Status", "Compliant") != "Compliant").astype(int) * RISK_WEIGHTS["overrun"],
        "Approval": df.get("Missing Board Approval", False).astype(int) * RISK_WEIGHTS["missing_board_approval"],
    })
    return factors.groupby("Vendor").mean().round(1)
