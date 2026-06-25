"""KPI card components."""

import streamlit as st

from utils.config import COLORS


KPI_CONFIG = [
    ("total", "Total Contracts", "📋", "neutral"),
    ("active", "Active Contracts", "✅", "up"),
    ("expiring_30", "Expiring in 30 Days", "⏰", "down"),
    ("expiring_90", "Expiring in 90 Days", "📅", "down"),
    ("auto_renew", "Auto-Renew", "🔄", "neutral"),
    ("high_risk", "High-Risk", "⚠️", "down"),
    ("sla_breaches", "SLA Breaches", "📉", "down"),
    ("overruns", "Contract Overruns", "💸", "down"),
    ("missing_approvals", "Missing Approvals", "❌", "down"),
]


def render_kpi_row(kpis: dict) -> None:
    """Render animated KPI cards in a 3-column grid."""
    for row_start in range(0, len(KPI_CONFIG), 3):
        cols = st.columns(3)
        for i, (key, label, icon, trend) in enumerate(KPI_CONFIG[row_start:row_start + 3]):
            with cols[i]:
                value = kpis.get(key, 0)
                trend_html = ""
                if trend == "up":
                    trend_html = "<div class='kpi-trend-up'>▲ Active</div>"
                elif trend == "down" and value > 0:
                    trend_html = "<div class='kpi-trend-down'>▼ Attention</div>"

                st.markdown(
                    f"""<div class="kpi-card">
                        <div class="kpi-icon">{icon}</div>
                        <div class="kpi-value">{value:,}</div>
                        <div class="kpi-label">{label}</div>
                        {trend_html}
                    </div>""",
                    unsafe_allow_html=True,
                )
