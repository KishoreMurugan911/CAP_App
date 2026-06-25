"""Excel upload validation and duplicate detection."""

from dataclasses import dataclass, field
from typing import Optional

import pandas as pd


@dataclass
class ValidationResult:
    valid: bool
    df: Optional[pd.DataFrame] = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    duplicates: list[str] = field(default_factory=list)


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df


def _check_required_columns(df: pd.DataFrame, required: list[str]) -> list[str]:
    missing = [c for c in required if c not in df.columns]
    return [f"Missing required column: {c}" for c in missing]


def _detect_duplicates(df: pd.DataFrame, id_col: str) -> list[str]:
    if id_col not in df.columns:
        return []
    dupes = df[df[id_col].duplicated(keep=False)][id_col].unique().tolist()
    return [str(d) for d in dupes]


def validate_contracts(df: pd.DataFrame) -> ValidationResult:
    result = ValidationResult(valid=False)
    if df is None or df.empty:
        result.errors.append("Uploaded file is empty.")
        return result

    df = _normalize_columns(df)
    result.errors.extend(_check_required_columns(df, [
        "Contract ID", "Contract Name", "Vendor", "Contract Value", "End Date",
    ]))
    if result.errors:
        return result

    result.duplicates = _detect_duplicates(df, "Contract ID")
    if result.duplicates:
        result.warnings.append(
            f"Duplicate Contract IDs found: {', '.join(result.duplicates[:10])}"
        )

    try:
        df["Contract Value"] = pd.to_numeric(df["Contract Value"], errors="coerce")
        df["Start Date"] = pd.to_datetime(df["Start Date"], errors="coerce")
        df["End Date"] = pd.to_datetime(df["End Date"], errors="coerce")
        if "SLA Target %" in df.columns:
            df["SLA Target %"] = pd.to_numeric(df["SLA Target %"], errors="coerce")
        if "SLA Actual %" in df.columns:
            df["SLA Actual %"] = pd.to_numeric(df["SLA Actual %"], errors="coerce")
    except Exception as exc:
        result.errors.append(f"Data type conversion failed: {exc}")
        return result

    null_values = df["Contract ID"].isna().sum()
    if null_values:
        result.errors.append(f"{null_values} rows have missing Contract ID.")

    if result.errors:
        return result

    result.valid = True
    result.df = df
    return result


def validate_purchase_orders(df: pd.DataFrame) -> ValidationResult:
    result = ValidationResult(valid=False)
    if df is None or df.empty:
        result.errors.append("Uploaded file is empty.")
        return result

    df = _normalize_columns(df)
    required = ["PO Number", "Contract ID", "PO Amount"]
    result.errors.extend(_check_required_columns(df, required))
    if result.errors:
        return result

    result.duplicates = _detect_duplicates(df, "PO Number")
    if result.duplicates:
        result.warnings.append(f"Duplicate PO Numbers: {', '.join(result.duplicates[:10])}")

    df["PO Amount"] = pd.to_numeric(df["PO Amount"], errors="coerce")
    result.valid = True
    result.df = df
    return result


def validate_payments(df: pd.DataFrame) -> ValidationResult:
    result = ValidationResult(valid=False)
    if df is None or df.empty:
        result.errors.append("Uploaded file is empty.")
        return result

    df = _normalize_columns(df)
    required = ["Payment ID", "Contract ID", "Payment Amount"]
    result.errors.extend(_check_required_columns(df, required))
    if result.errors:
        return result

    result.duplicates = _detect_duplicates(df, "Payment ID")
    if result.duplicates:
        result.warnings.append(f"Duplicate Payment IDs: {', '.join(result.duplicates[:10])}")

    df["Payment Amount"] = pd.to_numeric(df["Payment Amount"], errors="coerce")
    result.valid = True
    result.df = df
    return result


def validate_sla(df: pd.DataFrame) -> ValidationResult:
    result = ValidationResult(valid=False)
    if df is None or df.empty:
        result.errors.append("Uploaded file is empty.")
        return result

    df = _normalize_columns(df)
    required = ["Contract ID", "Month", "SLA Target", "SLA Actual"]
    result.errors.extend(_check_required_columns(df, required))
    if result.errors:
        return result

    df["SLA Target"] = pd.to_numeric(df["SLA Target"], errors="coerce")
    df["SLA Actual"] = pd.to_numeric(df["SLA Actual"], errors="coerce")
    result.valid = True
    result.df = df
    return result
