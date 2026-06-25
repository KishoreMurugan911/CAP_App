"""Expiry Monitoring view."""

import streamlit as st

from components.tables import render_aggrid_table
from components.ui import render_page_header
from utils.filters import render_global_filters


def render_expiry_monitoring(enriched_df):
    render_page_header(
        "Contract Validity Review",
        "Monitor expired and expiring contracts with countdown tracking",
    )

    if enriched_df.empty:
        st.warning("No contract data available.")
        return

    filtered = render_global_filters(enriched_df, key_prefix="exp")

    expiry_filter = st.multiselect(
        "Filter by Expiry Status",
        ["Expired", "Expiring in 30 Days", "Expiring in 60 Days", "Expiring in 90 Days"],
        default=["Expired", "Expiring in 30 Days", "Expiring in 60 Days", "Expiring in 90 Days"],
    )

    if expiry_filter and "Expiry Status" in filtered.columns:
        display = filtered[filtered["Expiry Status"].isin(expiry_filter)].copy()
    else:
        display = filtered.copy()

    cols = [c for c in [
        "Contract ID", "Contract Name", "Vendor", "Contract Owner",
        "End Date", "Days to Expiry", "Contract Value", "Expiry Status", "Risk Category",
    ] if c in display.columns]

    col1, col2, col3, col4 = st.columns(4)
    for col, status in zip([col1, col2, col3, col4],
                           ["Expired", "Expiring in 30 Days", "Expiring in 60 Days", "Expiring in 90 Days"]):
        count = len(display[display.get("Expiry Status", "") == status]) if "Expiry Status" in display.columns else 0
        with col:
            st.metric(status, count)

    st.markdown("### Expiring & Expired Contracts")
    render_aggrid_table(display[cols] if cols else display, risk_column="Expiry Status")
