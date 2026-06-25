"""Approval Compliance Review view."""

import streamlit as st

from components.tables import render_aggrid_table
from components.ui import render_page_header
from utils.filters import render_global_filters


def render_approval_review(enriched_df):
    render_page_header(
        "Approval Compliance Review",
        "Verify required approvals for contracts above threshold",
    )

    if enriched_df.empty:
        st.warning("No contract data available.")
        return

    threshold = st.session_state.get("approval_threshold", 1_000_000)
    st.info(f"Approval threshold: **${threshold:,.0f}** (configurable in Settings)")

    filtered = render_global_filters(enriched_df, key_prefix="approval")
    above = filtered[filtered.get("Above Threshold", False)].copy()

    missing = above[above.get("Missing Approvals", False)]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Above Threshold", len(above))
    with col2:
        st.metric("Missing Approvals", len(missing))
    with col3:
        compliant = len(above) - len(missing)
        st.metric("Compliant", compliant)

    matrix_cols = [c for c in [
        "Contract ID", "Contract Name", "Vendor", "Contract Value",
        "Legal Approval", "Legal Approved", "Board Approval", "Board Approved",
        "Missing Legal Approval", "Missing Board Approval", "Missing Approvals", "Risk Category",
    ] if c in above.columns]

    st.markdown("### Approval Matrix")
    render_aggrid_table(above[matrix_cols] if matrix_cols else above, risk_column="Risk Category")

    if not missing.empty:
        st.error(f"**{len(missing)}** high-value contracts have missing required approvals.")
