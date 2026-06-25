"""Global filter utilities."""

from typing import Optional

import pandas as pd
import streamlit as st


def render_global_filters(df: pd.DataFrame, key_prefix: str = "global") -> pd.DataFrame:
    """Render sidebar/global filters and return filtered dataframe."""
    if df.empty:
        return df

    st.markdown("##### 🔍 Advanced Filters")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        vendors = ["All"] + sorted(df["Vendor"].dropna().unique().tolist()) if "Vendor" in df.columns else ["All"]
        vendor = st.selectbox("Vendor", vendors, key=f"{key_prefix}_vendor")

        owners = ["All"] + sorted(df["Contract Owner"].dropna().unique().tolist()) if "Contract Owner" in df.columns else ["All"]
        owner = st.selectbox("Contract Owner", owners, key=f"{key_prefix}_owner")

    with col2:
        risks = ["All", "Low", "Medium", "High", "Critical"]
        risk = st.selectbox("Risk Rating", risks, key=f"{key_prefix}_risk")

        expiry_opts = ["All", "Expired", "Expiring in 30 Days", "Expiring in 60 Days", "Expiring in 90 Days", "Active"]
        expiry = st.selectbox("Expiry Period", expiry_opts, key=f"{key_prefix}_expiry")

    with col3:
        renew_opts = ["All", "Yes", "No"]
        auto_renew = st.selectbox("Auto Renew", renew_opts, key=f"{key_prefix}_renew")

        approval_opts = ["All", "Compliant", "Missing Approvals"]
        approval = st.selectbox("Approval Status", approval_opts, key=f"{key_prefix}_approval")

    with col4:
        min_val = float(df["Contract Value"].min()) if "Contract Value" in df.columns else 0
        max_val = float(df["Contract Value"].max()) if "Contract Value" in df.columns else 1_000_000
        value_range = st.slider(
            "Contract Value Range ($)",
            min_value=min_val,
            max_value=max(max_val, min_val + 1),
            value=(min_val, max_val),
            key=f"{key_prefix}_value",
        )

    filtered = df.copy()

    if vendor != "All" and "Vendor" in filtered.columns:
        filtered = filtered[filtered["Vendor"] == vendor]

    if owner != "All" and "Contract Owner" in filtered.columns:
        filtered = filtered[filtered["Contract Owner"] == owner]

    if risk != "All" and "Risk Category" in filtered.columns:
        filtered = filtered[filtered["Risk Category"] == risk]

    if expiry != "All" and "Expiry Status" in filtered.columns:
        if expiry == "Active":
            filtered = filtered[filtered["Expiry Status"] == "Active"]
        else:
            filtered = filtered[filtered["Expiry Status"] == expiry]

    if auto_renew != "All" and "Auto Renew Flag" in filtered.columns:
        flag = auto_renew == "Yes"
        filtered = filtered[filtered["Auto Renew Flag"] == flag]

    if approval != "All" and "Missing Approvals" in filtered.columns:
        if approval == "Compliant":
            filtered = filtered[~filtered["Missing Approvals"]]
        else:
            filtered = filtered[filtered["Missing Approvals"]]

    if "Contract Value" in filtered.columns:
        filtered = filtered[
            (filtered["Contract Value"] >= value_range[0]) &
            (filtered["Contract Value"] <= value_range[1])
        ]

    st.caption(f"Showing **{len(filtered)}** of **{len(df)}** contracts")
    return filtered
