"""SLA Performance Review view."""

import streamlit as st

from components.charts import chart_sla_compliance, chart_sla_trend, chart_vendor_sla_scorecard
from components.tables import render_aggrid_table
from components.ui import render_page_header
from utils.filters import render_global_filters


def render_sla_analysis(enriched_df, sla_df):
    render_page_header(
        "SLA Performance Review",
        "Compare SLA targets vs actuals, identify breaches and penalties",
    )

    if enriched_df.empty:
        st.warning("No contract data available.")
        return

    filtered = render_global_filters(enriched_df, key_prefix="sla")

    col1, col2, col3 = st.columns(3)
    breaches = filtered[filtered.get("SLA Breach", False)]
    repeated = filtered[filtered.get("Repeated SLA Failures", False)]
    penalties = filtered[filtered.get("Penalty Clause", "").astype(str).str.lower().isin(["yes", "y"]) & filtered.get("SLA Breach", False)]

    with col1:
        st.metric("SLA Breaches", len(breaches))
    with col2:
        st.metric("Repeated Failures", len(repeated))
    with col3:
        st.metric("Penalty Applicable", len(penalities))

    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.plotly_chart(chart_sla_compliance(filtered), use_container_width=True)
    with chart_col2:
        st.plotly_chart(chart_sla_trend(sla_df), use_container_width=True)

    st.plotly_chart(chart_vendor_sla_scorecard(filtered, sla_df), use_container_width=True)

    sla_display = filtered[[c for c in [
        "Contract ID", "Contract Name", "Vendor", "SLA Target %", "SLA Actual %",
        "SLA Breach", "Repeated SLA Failures", "Penalty Clause", "Risk Category",
    ] if c in filtered.columns]]

    st.markdown("### SLA Performance Details")
    render_aggrid_table(sla_display, risk_column="Risk Category")
