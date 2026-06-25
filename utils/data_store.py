"""Session state and data persistence."""

import logging
from typing import Any

import pandas as pd
import streamlit as st

logger = logging.getLogger(__name__)

EMPTY_DF = pd.DataFrame()


def init_session_state() -> None:
    """Initialize all session state keys with defaults."""
    defaults: dict[str, Any] = {
        "authenticated": False,
        "username": "",
        "contracts": EMPTY_DF.copy(),
        "purchase_orders": EMPTY_DF.copy(),
        "payments": EMPTY_DF.copy(),
        "sla_performance": EMPTY_DF.copy(),
        "enriched_contracts": EMPTY_DF.copy(),
        "audit_findings": [],
        "approval_threshold": 1_000_000,
        "upload_errors": {},
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_contracts() -> pd.DataFrame:
    return st.session_state.get("contracts", EMPTY_DF).copy()


def get_purchase_orders() -> pd.DataFrame:
    return st.session_state.get("purchase_orders", EMPTY_DF).copy()


def get_payments() -> pd.DataFrame:
    return st.session_state.get("payments", EMPTY_DF).copy()


def get_sla_performance() -> pd.DataFrame:
    return st.session_state.get("sla_performance", EMPTY_DF).copy()


def has_data() -> bool:
    return not get_contracts().empty


def set_dataframe(key: str, df: pd.DataFrame) -> None:
    st.session_state[key] = df
    logger.info("Updated session data: %s (%d rows)", key, len(df))
