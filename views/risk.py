"""Risk Scoring Engine view."""

import streamlit as st

from components.charts import chart_risk_heatmap
from components.tables import render_aggrid_table
from components.ui import render_page_header
from utils.config import RISK_WEIGHTS
from utils.filters import render_global_filters
from utils.risk_engine import get_risk_heatmap_data


def render_risk_scoring(enriched_df):
    render_page_header(
        "Risk Scoring Engine",
        "Automated contract risk assessment and ranking",
    )

    if enriched_df.empty:
        st.warning("No contract data available.")
        return

    filtered = render_global_filters(enriched_df, key_prefix="risk")

    with st.expander("Risk Scoring Methodology", expanded=False):
        st.markdown("**Risk Factors & Weights:**")
        for factor, weight in RISK_WEIGHTS.items():
            st.markdown(f"- {factor.replace('_', ' ').title()}: **{weight}** points")

    col1, col2, col3, col4 = st.columns(4)
    for col, cat in zip([col1, col2, col3, col4], ["Low", "Medium", "High", "Critical"]):
        count = len(filtered[filtered.get("Risk Category") == cat])
        with col:
            st.metric(cat, count)

    st.plotly_chart(chart_risk_heatmap(filtered), use_container_width=True)

    ranking_cols = [c for c in [
        "Contract ID", "Contract Name", "Vendor", "Contract Value",
        "Risk Score", "Risk Category", "Signature Missing", "Is Expired",
        "SLA Breach", "Overrun Status", "Missing Board Approval",
    ] if c in filtered.columns]

    ranked = filtered.sort_values("Risk Score", ascending=False) if "Risk Score" in filtered.columns else filtered

    st.markdown("### Risk Ranking Table")
    render_aggrid_table(ranked[ranking_cols] if ranking_cols else ranked, risk_column="Risk Category")

    st.markdown("### Top 10 High-Risk Contracts")
    top10 = ranked.head(10)
    render_aggrid_table(top10[ranking_cols] if ranking_cols else top10, risk_column="Risk Category", height=350)
