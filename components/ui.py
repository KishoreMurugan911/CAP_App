"""Premium UI styling and shared components."""

import base64
from pathlib import Path

import streamlit as st

from utils.config import COLORS, LOGO_PATH


def load_css() -> None:
    """Inject custom CSS for glassmorphism enterprise theme."""
    css_path = Path(__file__).resolve().parent.parent / "assets" / "styles.css"
    if css_path.exists():
        with open(css_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.markdown(f"<style>{_inline_css()}</style>", unsafe_allow_html=True)


def _inline_css() -> str:
    return f"""
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }}

    .stApp {{
        background: linear-gradient(135deg, {COLORS['primary']} 0%, #1a2744 50%, {COLORS['secondary']} 100%);
        background-attachment: fixed;
    }}

    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
        border-right: 1px solid rgba(59, 130, 246, 0.2);
    }}

    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] label {{
        color: {COLORS['text']} !important;
    }}

    .glass-card {{
        background: rgba(30, 41, 59, 0.55);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(59, 130, 246, 0.25);
        border-radius: 16px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    }}

    .glass-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(59, 130, 246, 0.15);
        border-color: rgba(59, 130, 246, 0.4);
    }}

    .kpi-card {{
        background: linear-gradient(135deg, rgba(30,41,59,0.8) 0%, rgba(15,23,42,0.9) 100%);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 14px;
        padding: 1.2rem;
        text-align: center;
        transition: all 0.25s ease;
        min-height: 130px;
    }}

    .kpi-card:hover {{
        transform: scale(1.02);
        border-color: {COLORS['accent']};
        box-shadow: 0 0 24px rgba(59, 130, 246, 0.25);
    }}

    .kpi-value {{
        font-size: 2rem;
        font-weight: 700;
        color: {COLORS['text']};
        line-height: 1.2;
    }}

    .kpi-label {{
        font-size: 0.8rem;
        color: {COLORS['muted']};
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.4rem;
    }}

    .kpi-icon {{
        font-size: 1.5rem;
        margin-bottom: 0.3rem;
    }}

    .kpi-trend-up {{ color: {COLORS['success']}; font-size: 0.75rem; }}
    .kpi-trend-down {{ color: {COLORS['critical']}; font-size: 0.75rem; }}

    .dashboard-header {{
        background: rgba(30, 41, 59, 0.6);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 1rem;
    }}

    .page-title {{
        font-size: 1.75rem;
        font-weight: 700;
        color: {COLORS['text']};
        margin: 0;
    }}

    .page-subtitle {{
        color: {COLORS['muted']};
        font-size: 0.95rem;
        margin: 0;
    }}

    .status-critical {{ background: rgba(239,68,68,0.2); color: {COLORS['critical']}; padding: 4px 10px; border-radius: 6px; font-weight: 600; }}
    .status-warning {{ background: rgba(245,158,11,0.2); color: {COLORS['warning']}; padding: 4px 10px; border-radius: 6px; font-weight: 600; }}
    .status-success {{ background: rgba(34,197,94,0.2); color: {COLORS['success']}; padding: 4px 10px; border-radius: 6px; font-weight: 600; }}

    .login-container {{
        max-width: 420px;
        margin: 3rem auto;
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 20px;
        padding: 2.5rem;
        text-align: center;
        box-shadow: 0 20px 60px rgba(0,0,0,0.4);
    }}

    div[data-testid="stMetricValue"] {{
        font-size: 1.8rem;
    }}

    .stButton > button {{
        background: linear-gradient(135deg, {COLORS['accent']} 0%, #2563EB 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;
    }}

    .stButton > button:hover {{
        box-shadow: 0 4px 16px rgba(59, 130, 246, 0.4);
        transform: translateY(-1px);
    }}

    [data-testid="stDataFrame"] {{
        border-radius: 12px;
        overflow: hidden;
    }}
    """


def get_logo_base64() -> str:
    if LOGO_PATH.exists():
        with open(LOGO_PATH, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""


def render_logo(width: int = 180, centered: bool = False) -> None:
    """Display company logo."""
    if LOGO_PATH.exists():
        align = "margin: 0 auto;" if centered else ""
        st.image(str(LOGO_PATH), width=width)
    else:
        st.markdown(f"<h2 style='color:{COLORS['accent']}'>CAP AI</h2>", unsafe_allow_html=True)


def render_sidebar_header() -> None:
    """Sidebar branding with logo."""
    render_logo(width=160)
    st.markdown(
        f"<p style='color:{COLORS['muted']}; font-size:0.85rem; margin-top:-0.5rem;'>"
        "Contract Governance Platform</p>",
        unsafe_allow_html=True,
    )
    st.divider()


def render_page_header(title: str, subtitle: str = "") -> None:
    """Dashboard page header with logo."""
    col1, col2 = st.columns([1, 5])
    with col1:
        render_logo(width=80)
    with col2:
        st.markdown(f"<p class='page-title'>{title}</p>", unsafe_allow_html=True)
        if subtitle:
            st.markdown(f"<p class='page-subtitle'>{subtitle}</p>", unsafe_allow_html=True)


def render_login_page() -> bool:
    """Render login form. Returns True if authenticated."""
    load_css()
    st.markdown("<div class='login-container'>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        render_logo(width=200)
        st.markdown(
            f"<h2 style='color:{COLORS['text']}; text-align:center;'>Contract & Agreement Review</h2>"
            f"<p style='color:{COLORS['muted']}; text-align:center;'>Enterprise Contract Governance Platform</p>",
            unsafe_allow_html=True,
        )
        st.markdown("---")
        username = st.text_input("Username", placeholder="Enter your username", key="login_user")
        password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_pass")

        if st.button("Sign In", use_container_width=True, type="primary"):
            if username and password:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Please enter username and password.")

        st.caption("Demo mode: any credentials accepted")

    st.markdown("</div>", unsafe_allow_html=True)
    return st.session_state.get("authenticated", False)


def status_badge(status: str) -> str:
    """Return HTML badge for status."""
    mapping = {
        "Critical": "status-critical",
        "Warning": "status-warning",
        "Compliant": "status-success",
        "Low": "status-success",
        "Medium": "status-warning",
        "High": "status-critical",
    }
    css = mapping.get(status, "status-warning")
    return f"<span class='{css}'>{status}</span>"
