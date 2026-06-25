"""Executive Dashboard view."""

import streamlit as st

from components.charts import (
    chart_approval_compliance,
    chart_auto_renew,
    chart_expiry_timeline,
    chart_risk_heatmap,
    chart_sla_compliance,
    chart_spend_vs_value,
    chart_status_distribution,
    chart_value_by_vendor,
)
from components.kpi_cards import render_kpi_row
from components.ui import render_page_header
from utils.filters import render_global_filters
from utils.processors import compute_kpis


def render_dashboard(enriched_df):
    render_page_header(
        "Executive Dashboard",
        "Real-time contract governance analytics and KPI monitoring",
    )

    if enriched_df.empty:
        st.warning("Upload contract data to view the dashboard. Go to **Contract Review** to get started.")
        return

    filtered = render_global_filters(enriched_df, key_prefix="dash")
    kpis = compute_kpis(filtered)
    render_kpi_row(kpis)

    st.markdown("---")
    st.markdown("### 📊 Interactive Analytics")

    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        st.plotly_chart(chart_status_distribution(filtered), use_container_width=True)
    with row1_col2:
        st.plotly_chart(chart_expiry_timeline(filtered), use_container_width=True)

    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        st.plotly_chart(chart_auto_renew(filtered), use_container_width=True)
    with row2_col2:
        st.plotly_chart(chart_value_by_vendor(filtered), use_container_width=True)

    row3_col1, row3_col2 = st.columns(2)
    with row3_col1:
        st.plotly_chart(chart_sla_compliance(filtered), use_container_width=True)
    with row3_col2:
        st.plotly_chart(chart_approval_compliance(filtered), use_container_width=True)

    row4_col1, row4_col2 = st.columns(2)
    with row4_col1:
        st.plotly_chart(chart_risk_heatmap(filtered), use_container_width=True)
    with row4_col2:
        display = filtered.head(15) if len(filtered) > 15 else filtered
        st.plotly_chart(chart_spend_vs_value(display), use_container_width=True)
