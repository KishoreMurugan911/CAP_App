"""Spend Analysis — Contract Value vs PO vs Payments."""

import streamlit as st

from components.charts import chart_spend_vs_value
from components.tables import render_aggrid_table
from components.ui import render_page_header
from utils.filters import render_global_filters


def render_spend_analysis(enriched_df):
    render_page_header(
        "Contract Value vs PO vs Payments",
        "Reconciliation analysis with overrun detection and drill-down",
    )

    if enriched_df.empty:
        st.warning("No contract data available.")
        return

    filtered = render_global_filters(enriched_df, key_prefix="spend")

    overruns = filtered[filtered.get("Overrun Status", "Compliant") != "Compliant"]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Overruns", len(overruns))
    with col2:
        critical = len(filtered[filtered.get("Overrun Status") == "Critical"])
        st.metric("Critical (Payment > Value)", critical)
    with col3:
        warning = len(filtered[filtered.get("Overrun Status") == "Warning"])
        st.metric("Warning (PO > Value)", warning)

    display = filtered[[c for c in [
        "Contract ID", "Contract Name", "Vendor", "Contract Value",
        "PO Total", "Payments Total", "PO Variance", "Payment Variance",
        "PO Overrun %", "Payment Overrun %", "Overrun Status", "Risk Category",
    ] if c in filtered.columns]].copy()

    st.plotly_chart(chart_spend_vs_value(filtered.head(20)), use_container_width=True)

    st.markdown("### Reconciliation Table")
    render_aggrid_table(display, risk_column="Overrun Status")

    if not overruns.empty:
        st.markdown("### Overrun Drill-Down")
        for _, row in overruns.iterrows():
            status = row.get("Overrun Status", "")
            icon = "🔴" if status == "Critical" else "🟡"
            st.markdown(
                f"{icon} **{row.get('Contract ID')}** — {row.get('Contract Name', '')}: "
                f"Value ${row.get('Contract Value', 0):,.0f} | "
                f"PO ${row.get('PO Total', 0):,.0f} | "
                f"Payments ${row.get('Payments Total', 0):,.0f} | "
                f"Variance ${row.get('Payment Variance', row.get('PO Variance', 0)):,.0f}"
            )
