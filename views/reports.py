"""PDF & Excel Reporting view."""

from datetime import datetime

import streamlit as st

from components.ui import render_logo, render_page_header
from utils.audit_findings import generate_findings
from utils.processors import compute_kpis
from utils.reporting import generate_excel_report, generate_pdf_report


def render_reports(enriched_df):
    render_page_header(
        "Executive Reports",
        "Generate branded PDF and Excel reports with findings and recommendations",
    )

    if enriched_df.empty:
        st.warning("No contract data available. Upload data to generate reports.")
        return

    kpis = compute_kpis(enriched_df)
    findings = generate_findings(enriched_df)

    col1, col2 = st.columns([1, 3])
    with col1:
        render_logo(width=120)
    with col2:
        st.markdown("### Report Preview")
        st.markdown(f"**Report Date:** {datetime.now().strftime('%B %d, %Y')}")
        st.markdown(f"**Contracts Analyzed:** {kpis.get('total', 0)}")
        st.markdown(f"**Audit Findings:** {len(findings)}")

    st.markdown("---")
    st.markdown("#### KPI Summary")
    kpi_cols = st.columns(3)
    for i, (key, val) in enumerate(kpis.items()):
        with kpi_cols[i % 3]:
            st.metric(key.replace("_", " ").title(), val)

    st.markdown("---")
    col_pdf, col_excel = st.columns(2)

    with col_pdf:
        if st.button("📄 Generate PDF Report", use_container_width=True, type="primary"):
            with st.spinner("Generating PDF..."):
                pdf_bytes = generate_pdf_report(enriched_df, kpis, findings)
                st.download_button(
                    "Download PDF",
                    data=pdf_bytes,
                    file_name=f"contract_review_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )

    with col_excel:
        if st.button("📊 Generate Excel Report", use_container_width=True, type="primary"):
            with st.spinner("Generating Excel..."):
                excel_bytes = generate_excel_report(enriched_df, kpis, findings)
                st.download_button(
                    "Download Excel",
                    data=excel_bytes,
                    file_name=f"contract_review_report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )

    st.markdown("---")
    st.markdown("#### PowerPoint-Ready Tables")
    st.caption("Excel report includes dedicated sheets formatted for PowerPoint import.")

    if findings:
        st.markdown("**Sample Findings Preview:**")
        for f in findings[:5]:
            st.markdown(f"- **{f.category}:** {f.finding}")
