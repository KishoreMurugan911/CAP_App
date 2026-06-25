"""Auto-Renewal Monitoring view."""

import streamlit as st

from components.tables import render_aggrid_table
from components.ui import render_page_header
from utils.filters import render_global_filters


def render_auto_renewals(enriched_df):
    render_page_header(
        "Auto-Renewal Monitoring",
        "Track auto-renew contracts, notice periods, and required actions",
    )

    if enriched_df.empty:
        st.warning("No contract data available.")
        return

    filtered = render_global_filters(enriched_df, key_prefix="renew")
    auto = filtered[filtered.get("Auto Renew Flag", False)].copy()

    st.metric("Auto-Renew Contracts", len(auto))

    if auto.empty:
        st.info("No auto-renew contracts found.")
        return

    action_cols = [c for c in [
        "Contract ID", "Contract Name", "Vendor", "Renewal Date",
        "Notice Deadline", "Days to Expiry", "Notice Alert", "Contract Owner", "Risk Category",
    ] if c in auto.columns]

    action = auto[action_cols].copy()
    action["Status"] = action.apply(
        lambda r: "Action Required" if r.get("Notice Alert") else "Monitoring",
        axis=1,
    )

    st.markdown("### Action Required Table")
    render_aggrid_table(action.rename(columns={
        "Contract Name": "Contract",
    }), risk_column="Status")

    alerts = action[action["Status"] == "Action Required"]
    if not alerts.empty:
        st.warning(f"**{len(alerts)}** contracts require renewal notice action.")
