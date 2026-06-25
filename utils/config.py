"""Application configuration and theme constants."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
TEMPLATES_DIR = BASE_DIR / "templates"

# Logo: prefer local assets, fallback to bundled upload path
_LOGO_CANDIDATES = [
    ASSETS_DIR / "logo.png",
    Path(r"C:\Users\Admin\.cursor\projects\empty-window\assets\c__Users_Admin_AppData_Roaming_Cursor_User_workspaceStorage_empty-window_images_cap-ai-logo-215b4d96-a722-4235-a4e1-b309d903a8ff.png"),
]
LOGO_PATH = next((p for p in _LOGO_CANDIDATES if p.exists()), _LOGO_CANDIDATES[0])

# Corporate theme palette
COLORS = {
    "primary": "#0F172A",
    "secondary": "#1E293B",
    "accent": "#3B82F6",
    "success": "#22C55E",
    "warning": "#F59E0B",
    "critical": "#EF4444",
    "text": "#F8FAFC",
    "muted": "#94A3B8",
}

PLOTLY_TEMPLATE = {
    "layout": {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(15,23,42,0.4)",
        "font": {"color": "#F8FAFC", "family": "Segoe UI, sans-serif"},
        "colorway": ["#3B82F6", "#22C55E", "#F59E0B", "#EF4444", "#8B5CF6", "#06B6D4"],
        "margin": {"l": 40, "r": 20, "t": 50, "b": 40},
        "xaxis": {"gridcolor": "rgba(148,163,184,0.15)", "zerolinecolor": "rgba(148,163,184,0.2)"},
        "yaxis": {"gridcolor": "rgba(148,163,184,0.15)", "zerolinecolor": "rgba(148,163,184,0.2)"},
        "legend": {"bgcolor": "rgba(15,23,42,0.6)", "bordercolor": "rgba(59,130,246,0.3)"},
    }
}

# Required columns per upload type
CONTRACTS_COLUMNS = [
    "Contract ID", "Contract Name", "Vendor", "Contract Value",
    "Start Date", "End Date", "Auto Renew", "Signature Status",
    "Legal Approval", "Board Approval", "SLA Target %", "SLA Actual %",
    "Penalty Clause", "Contract Owner",
]

PO_COLUMNS = ["PO Number", "Contract ID", "PO Amount"]
PAYMENTS_COLUMNS = ["Payment ID", "Contract ID", "Payment Amount"]
SLA_COLUMNS = ["Contract ID", "Month", "SLA Target", "SLA Actual"]

# Risk scoring weights
RISK_WEIGHTS = {
    "signature_missing": 20,
    "expired": 25,
    "auto_renew": 10,
    "sla_breach": 15,
    "overrun": 20,
    "missing_board_approval": 10,
}

DEFAULT_APPROVAL_THRESHOLD = 1_000_000
NOTICE_PERIOD_DAYS = 30

MENU_ITEMS = [
    "Dashboard",
    "Contract Review",
    "Signature Review",
    "Expiry Monitoring",
    "Auto Renewals",
    "SLA Analysis",
    "Spend Analysis",
    "Approval Review",
    "Risk Scoring",
    "Audit Findings",
    "Reports",
    "Settings",
]

MENU_ICONS = [
    "house", "file-earmark-text", "pen", "calendar-event", "arrow-repeat",
    "graph-up", "currency-dollar", "check2-square", "exclamation-triangle",
    "clipboard-data", "download", "gear",
]
