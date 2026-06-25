"""Excel Upload Center view."""

import io
from pathlib import Path

import pandas as pd
import streamlit as st

from components.ui import render_page_header
from utils.config import TEMPLATES_DIR
from utils.data_store import set_dataframe
from utils.validators import (
    validate_contracts,
    validate_payments,
    validate_purchase_orders,
    validate_sla,
)

UPLOAD_TYPES = {
    "Contracts Master": ("contracts", "contracts_master.xlsx", validate_contracts),
    "Purchase Orders": ("purchase_orders", "purchase_orders.xlsx", validate_purchase_orders),
    "Payments": ("payments", "payments.xlsx", validate_payments),
    "SLA Performance": ("sla_performance", "sla_performance.xlsx", validate_sla),
}


def _template_download(filename: str, label: str) -> None:
    path = TEMPLATES_DIR / filename
    if path.exists():
        with open(path, "rb") as f:
            st.download_button(
                f"📥 Download {label} Template",
                data=f.read(),
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )


def render_upload_center():
    render_page_header(
        "Contract Review — Excel Upload Center",
        "Upload, validate, and manage contract data sources",
    )

    tabs = st.tabs(["Contracts Master", "Purchase Orders", "Payments", "SLA Performance"])

    for tab, (label, (key, template, validator)) in zip(tabs, UPLOAD_TYPES.items()):
        with tab:
            st.markdown(f"#### {label}")
            _template_download(template, label)

            uploaded = st.file_uploader(
                f"Drag and drop {label} file",
                type=["xlsx", "xls"],
                key=f"upload_{key}",
            )

            if uploaded:
                try:
                    df = pd.read_excel(uploaded)
                    result = validator(df)

                    if result.errors:
                        st.error("**Validation Errors:**")
                        for err in result.errors:
                            st.markdown(f"- {err}")

                    if result.warnings:
                        st.warning("**Warnings:**")
                        for warn in result.warnings:
                            st.markdown(f"- {warn}")

                    if result.duplicates:
                        st.warning(f"**Duplicates detected:** {', '.join(result.duplicates)}")

                    if result.valid and result.df is not None:
                        set_dataframe(key, result.df)
                        st.success(f"Successfully loaded **{len(result.df)}** records.")
                        st.dataframe(result.df.head(10), use_container_width=True)

                except Exception as exc:
                    st.error(f"Failed to process file: {exc}")

            current = st.session_state.get(key, pd.DataFrame())
            if not current.empty:
                st.info(f"Current dataset: **{len(current)}** records loaded.")

    st.markdown("---")
    st.markdown("#### Quick Load Sample Data")
    if st.button("Load All Sample Templates", type="primary"):
        for _label, (key, template, validator) in UPLOAD_TYPES.items():
            path = TEMPLATES_DIR / template
            if path.exists():
                result = validator(pd.read_excel(path))
                if result.valid and result.df is not None:
                    set_dataframe(key, result.df)
        st.success("Sample data loaded successfully!")
        st.rerun()
