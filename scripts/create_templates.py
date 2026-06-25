"""Generate sample Excel templates."""

from pathlib import Path

import pandas as pd

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


def create_templates() -> None:
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

    contracts = pd.DataFrame([
        {"Contract ID": "C-101", "Contract Name": "Cloud Infrastructure Services", "Vendor": "TechCorp Inc",
         "Contract Value": 2500000, "Start Date": "2024-01-01", "End Date": "2026-12-31",
         "Auto Renew": "Y", "Signature Status": "Signed", "Legal Approval": "Yes", "Board Approval": "Yes",
         "SLA Target %": 99.5, "SLA Actual %": 99.8, "Penalty Clause": "Yes", "Contract Owner": "John Smith"},
        {"Contract ID": "C-102", "Contract Name": "Managed Security Services", "Vendor": "SecureNet Ltd",
         "Contract Value": 850000, "Start Date": "2023-06-01", "End Date": "2025-06-30",
         "Auto Renew": "N", "Signature Status": "Unsigned", "Legal Approval": "Yes", "Board Approval": "No",
         "SLA Target %": 99.0, "SLA Actual %": 97.5, "Penalty Clause": "Yes", "Contract Owner": "Jane Doe"},
        {"Contract ID": "C-103", "Contract Name": "Office Supplies Agreement", "Vendor": "SupplyCo",
         "Contract Value": 120000, "Start Date": "2024-03-01", "End Date": "2025-02-28",
         "Auto Renew": "Y", "Signature Status": "Pending", "Legal Approval": "Yes", "Board Approval": "N/A",
         "SLA Target %": 95.0, "SLA Actual %": 96.0, "Penalty Clause": "No", "Contract Owner": "Mike Johnson"},
        {"Contract ID": "C-104", "Contract Name": "ERP Implementation", "Vendor": "EnterpriseSoft",
         "Contract Value": 5200000, "Start Date": "2022-01-01", "End Date": "2024-06-30",
         "Auto Renew": "N", "Signature Status": "Signed", "Legal Approval": "Yes", "Board Approval": "Yes",
         "SLA Target %": 98.0, "SLA Actual %": 94.0, "Penalty Clause": "Yes", "Contract Owner": "Sarah Lee"},
        {"Contract ID": "C-105", "Contract Name": "Facilities Management", "Vendor": "BuildRight Co",
         "Contract Value": 680000, "Start Date": "2024-07-01", "End Date": "2025-07-31",
         "Auto Renew": "Y", "Signature Status": "Signed", "Legal Approval": "Yes", "Board Approval": "No",
         "SLA Target %": 97.0, "SLA Actual %": 98.5, "Penalty Clause": "No", "Contract Owner": "Tom Wilson"},
    ])
    contracts.to_excel(TEMPLATES_DIR / "contracts_master.xlsx", index=False)

    pos = pd.DataFrame([
        {"PO Number": "PO-1001", "Contract ID": "C-101", "PO Amount": 800000},
        {"PO Number": "PO-1002", "Contract ID": "C-101", "PO Amount": 600000},
        {"PO Number": "PO-1003", "Contract ID": "C-102", "PO Amount": 950000},
        {"PO Number": "PO-1004", "Contract ID": "C-104", "PO Amount": 6100000},
        {"PO Number": "PO-1005", "Contract ID": "C-105", "PO Amount": 350000},
    ])
    pos.to_excel(TEMPLATES_DIR / "purchase_orders.xlsx", index=False)

    payments = pd.DataFrame([
        {"Payment ID": "PAY-001", "Contract ID": "C-101", "Payment Amount": 750000},
        {"Payment ID": "PAY-002", "Contract ID": "C-101", "Payment Amount": 500000},
        {"Payment ID": "PAY-003", "Contract ID": "C-102", "Payment Amount": 1000000},
        {"Payment ID": "PAY-004", "Contract ID": "C-104", "Payment Amount": 5500000},
        {"Payment ID": "PAY-005", "Contract ID": "C-105", "Payment Amount": 200000},
    ])
    payments.to_excel(TEMPLATES_DIR / "payments.xlsx", index=False)

    sla = pd.DataFrame([
        {"Contract ID": "C-101", "Month": "2025-01", "SLA Target": 99.5, "SLA Actual": 99.8},
        {"Contract ID": "C-101", "Month": "2025-02", "SLA Target": 99.5, "SLA Actual": 99.6},
        {"Contract ID": "C-102", "Month": "2025-01", "SLA Target": 99.0, "SLA Actual": 97.5},
        {"Contract ID": "C-102", "Month": "2025-02", "SLA Target": 99.0, "SLA Actual": 96.8},
        {"Contract ID": "C-104", "Month": "2025-01", "SLA Target": 98.0, "SLA Actual": 94.0},
        {"Contract ID": "C-104", "Month": "2025-02", "SLA Target": 98.0, "SLA Actual": 93.5},
        {"Contract ID": "C-105", "Month": "2025-01", "SLA Target": 97.0, "SLA Actual": 98.5},
    ])
    sla.to_excel(TEMPLATES_DIR / "sla_performance.xlsx", index=False)

    print(f"Templates created in {TEMPLATES_DIR}")


if __name__ == "__main__":
    create_templates()
