# Contract & Agreement Review Dashboard

Enterprise-grade Streamlit application for contract governance, audit, procurement, legal, and compliance teams. Built by **CAP AI**.

## Features

- **Executive Dashboard** — KPI cards, 8 interactive Plotly charts, global filters
- **Excel Upload Center** — Drag-and-drop uploads with validation, duplicate detection, templates
- **Signature Review** — Unsigned contract identification with risk levels
- **Expiry Monitoring** — Expired and expiring contract tracking
- **Auto-Renewal Monitoring** — Notice period alerts and action tables
- **SLA Analysis** — Gauge charts, trends, vendor scorecards
- **Spend Analysis** — Contract vs PO vs Payment reconciliation
- **Approval Compliance** — Configurable threshold approval matrix
- **Risk Scoring Engine** — Weighted 0–100 scoring with heatmap
- **Audit Findings** — Automated findings with recommendations
- **Reports** — Branded PDF and Excel export with logo

## Folder Structure

```
contract-review-dashboard/
├── app.py                  # Main Streamlit entry point
├── requirements.txt
├── README.md
├── assets/
│   ├── logo.png            # CAP AI company logo
│   └── styles.css          # Premium glassmorphism theme
├── components/
│   ├── ui.py               # CSS, logo, login, headers
│   ├── kpi_cards.py        # Animated KPI cards
│   ├── charts.py           # Plotly enterprise charts
│   └── tables.py           # AgGrid tables
├── utils/
│   ├── config.py           # Theme, columns, risk weights
│   ├── data_store.py       # Session state management
│   ├── validators.py       # Upload validation
│   ├── processors.py       # Data enrichment & KPIs
│   ├── risk_engine.py      # Risk scoring
│   ├── audit_findings.py   # Findings generator
│   ├── filters.py          # Global filters
│   └── reporting.py        # PDF & Excel reports
├── views/                  # Page modules (12 screens)
├── templates/              # Sample Excel templates
├── scripts/
│   └── create_templates.py # Regenerate sample data
└── .streamlit/
    └── config.toml
```

## Quick Start

### 1. Prerequisites

- Python 3.10 or higher
- pip

### 2. Installation

```bash
cd contract-review-dashboard
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
python scripts/create_templates.py
```

### 3. Run the Application

```bash
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

### 4. Demo Login

Any username and password will authenticate (demo mode).

### 5. Load Sample Data

1. Navigate to **Contract Review**
2. Click **Load All Sample Templates**
3. Return to **Dashboard** to explore analytics

## Deployment

### Streamlit Community Cloud

1. Push the repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo and set main file to `app.py`
4. Deploy

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
docker build -t cap-ai-contract-dashboard .
docker run -p 8501:8501 cap-ai-contract-dashboard
```

### Azure / AWS / On-Premises

Run behind a reverse proxy (nginx, IIS) with HTTPS:

```bash
streamlit run app.py --server.port=8501 --server.address=0.0.0.0
```

For production, integrate SSO (Azure AD, Okta) by replacing the demo login in `components/ui.py`.

## Logo Integration

Place your company logo at `assets/logo.png`. The logo appears in:

- Sidebar header
- Login page
- Dashboard page headers
- PDF and Excel reports

For best results, use a **PNG with transparent background**.

## Configuration

| Setting | Location | Default |
|---------|----------|---------|
| Approval threshold | Settings page | $1,000,000 |
| Risk weights | `utils/config.py` | See RISK_WEIGHTS |
| Notice period | `utils/config.py` | 30 days |
| Theme colors | `utils/config.py` | Corporate blue |

## Technology Stack

- Streamlit, Pandas, NumPy, OpenPyXL, XlsxWriter
- Plotly, Streamlit AgGrid, Streamlit Option Menu, Streamlit Extras
- ReportLab (PDF generation)

## License

Proprietary — CAP AI. Internal use only unless otherwise licensed.
