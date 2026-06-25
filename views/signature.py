"""Signature Review view."""

import streamlit as st

from components.tables import render_aggrid_table
from components.ui import render_page_header, status_badge
from utils.filters import render_global_filters


def render_signature_review(enriched_df):
    render_page_header(
        "Contract Signature Review",
        "Identify unsigned contracts and missing authorized signatories",
    )

    if enriched_df.empty:
        st.warning("No contract data available.")
        return

    filtered = render_global_filters(enriched_df, key_prefix="sig")
    unsigned = filtered[filtered.get("Signature Missing", False)].copy()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Unsigned Contracts", len(unsigned))
    with col2:
        critical = len(unsigned[unsigned.get("Risk Category", "") == "Critical"])
        st.metric("Critical Risk", critical)
    with col3:
        avg_days = unsigned["Days to Expiry"].mean() if not unsigned.empty and "Days to Expiry" in unsigned.columns else 0
        st.metric("Avg Days Pending", f"{avg_days:.0f}" if avg_days else "N/A")

    if unsigned.empty:
        st.success("All contracts have valid signatures.")
        return

    display = unsigned[[
        c for c in [
            "Contract ID", "Contract Name", "Vendor", "Contract Owner",
            "Signature Status", "Days to Expiry", "Contract Value", "Risk Category",
        ] if c in unsigned.columns
    ]].copy()

    display["Risk Level"] = display.get("Risk Category", "Warning")
    display["Days Pending"] = display.get("Days to Expiry", 0).apply(
        lambda d: max(0, -d) if d < 0 else abs(d) if d else 0
    )

    st.markdown("### Missing Signatures")
    render_aggrid_table(display, risk_column="Risk Level")
