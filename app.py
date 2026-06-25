"""Contract & Agreement Review Dashboard — Main Application."""

import logging
import sys
from pathlib import Path

import streamlit as st
from streamlit_option_menu import option_menu

# Ensure project root is on path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from components.ui import load_css, render_login_page, render_sidebar_header
from utils.config import MENU_ICONS, MENU_ITEMS
from utils.data_store import (
    get_contracts,
    get_payments,
    get_purchase_orders,
    get_sla_performance,
    init_session_state,
)
from utils.processors import enrich_contracts
from views.approval import render_approval_review
from views.audit import render_audit_findings
from views.auto_renew import render_auto_renewals
from views.dashboard import render_dashboard
from views.expiry import render_expiry_monitoring
from views.reports import render_reports
from views.risk import render_risk_scoring
from views.settings import render_settings
from views.signature import render_signature_review
from views.sla import render_sla_analysis
from views.spend import render_spend_analysis
from views.upload import render_upload_center

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="CAP AI — Contract & Agreement Review",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main():
    init_session_state()
    load_css()

    if not st.session_state.get("authenticated"):
        render_login_page()
        return

    with st.sidebar:
        render_sidebar_header()
        selected = option_menu(
            menu_title=None,
            options=MENU_ITEMS,
            icons=MENU_ICONS,
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0", "background-color": "transparent"},
                "icon": {"color": "#3B82F6", "font-size": "16px"},
                "nav-link": {
                    "font-size": "14px",
                    "text-align": "left",
                    "margin": "2px 0",
                    "padding": "10px 14px",
                    "color": "#F8FAFC",
                    "border-radius": "8px",
                },
                "nav-link-selected": {
                    "background-color": "rgba(59, 130, 246, 0.25)",
                    "border-left": "3px solid #3B82F6",
                    "color": "#F8FAFC",
                },
            },
        )

        st.divider()
        user = st.session_state.get("username", "User")
        st.caption(f"Signed in as **{user}**")
        if st.button("Sign Out", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.username = ""
            st.rerun()

    threshold = st.session_state.get("approval_threshold", 1_000_000)
    contracts = get_contracts()
    pos = get_purchase_orders()
    payments = get_payments()
    sla = get_sla_performance()

    enriched = enrich_contracts(contracts, pos, payments, sla, threshold)
    st.session_state.enriched_contracts = enriched

    page_map = {
        "Dashboard": lambda: render_dashboard(enriched),
        "Contract Review": render_upload_center,
        "Signature Review": lambda: render_signature_review(enriched),
        "Expiry Monitoring": lambda: render_expiry_monitoring(enriched),
        "Auto Renewals": lambda: render_auto_renewals(enriched),
        "SLA Analysis": lambda: render_sla_analysis(enriched, sla),
        "Spend Analysis": lambda: render_spend_analysis(enriched),
        "Approval Review": lambda: render_approval_review(enriched),
        "Risk Scoring": lambda: render_risk_scoring(enriched),
        "Audit Findings": lambda: render_audit_findings(enriched),
        "Reports": lambda: render_reports(enriched),
        "Settings": render_settings,
    }

    page_map.get(selected, lambda: render_dashboard(enriched))()


if __name__ == "__main__":
    main()
