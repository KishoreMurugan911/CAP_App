"""Audit Findings Generator view."""

import streamlit as st

from components.tables import render_aggrid_table
from components.ui import render_page_header, status_badge
from utils.audit_findings import findings_to_dataframe, generate_findings
from utils.filters import render_global_filters


def render_audit_findings(enriched_df):
    render_page_header(
        "Audit Findings Generator",
        "Automated audit findings with risk assessment and recommendations",
    )

    if enriched_df.empty:
        st.warning("No contract data available.")
        return

    filtered = render_global_filters(enriched_df, key_prefix="audit")
    findings = generate_findings(filtered)
    st.session_state.audit_findings = findings

    col1, col2, col3 = st.columns(3)
    critical = sum(1 for f in findings if f.severity == "Critical")
    warning = sum(1 for f in findings if f.severity == "Warning")
    with col1:
        st.metric("Total Findings", len(findings))
    with col2:
        st.metric("Critical", critical)
    with col3:
        st.metric("Warnings", warning)

    if not findings:
        st.success("No audit findings identified. All contracts appear compliant.")
        return

    for f in findings[:10]:
        severity_color = {"Critical": "🔴", "Warning": "🟡", "Info": "🔵"}.get(f.severity, "⚪")
        with st.expander(f"{severity_color} [{f.category}] {f.contract_id}", expanded=False):
            st.markdown(f"**Finding:** {f.finding}")
            st.markdown(f"**Risk:** {f.risk}")
            st.markdown(f"**Recommendation:** {f.recommendation}")

    st.markdown("### All Findings")
    findings_df = findings_to_dataframe(findings)
    render_aggrid_table(findings_df, risk_column="Severity")
