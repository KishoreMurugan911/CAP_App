"""Settings view."""

import streamlit as st

from components.ui import render_page_header
from utils.config import DEFAULT_APPROVAL_THRESHOLD


def render_settings():
    render_page_header("Settings", "Configure application preferences and thresholds")

    st.markdown("### Approval Threshold")
    threshold = st.number_input(
        "Contracts above this value require Legal and Board approval ($)",
        min_value=0,
        value=int(st.session_state.get("approval_threshold", DEFAULT_APPROVAL_THRESHOLD)),
        step=100000,
        format="%d",
    )
    st.session_state.approval_threshold = threshold

    st.markdown("### Display Preferences")
    st.checkbox("Show trend indicators on KPI cards", value=True, disabled=True,
                help="Enabled by default in premium theme")

    st.markdown("### Data Management")
    if st.button("Clear All Uploaded Data", type="secondary"):
        import pandas as pd
        for key in ["contracts", "purchase_orders", "payments", "sla_performance", "enriched_contracts"]:
            st.session_state[key] = pd.DataFrame()
        st.success("All data cleared.")
        st.rerun()

    st.markdown("### About")
    st.markdown(
        "**Contract & Agreement Review Dashboard** v1.0  \n"
        "Enterprise contract governance platform by **CAP AI**  \n"
        "Built with Streamlit • Plotly • AgGrid"
    )
