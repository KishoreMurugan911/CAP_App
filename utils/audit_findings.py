"""Automated audit findings generator."""

from dataclasses import dataclass
from typing import Optional

import pandas as pd


@dataclass
class AuditFinding:
    finding: str
    risk: str
    recommendation: str
    category: str
    contract_id: str
    severity: str


def generate_findings(df: pd.DataFrame) -> list[AuditFinding]:
    """Generate audit findings from enriched contract data."""
    if df.empty:
        return []

    findings: list[AuditFinding] = []

    for _, row in df.iterrows():
        cid = str(row.get("Contract ID", ""))
        name = str(row.get("Contract Name", cid))

        if row.get("Signature Missing"):
            findings.append(AuditFinding(
                finding=f"Contract {cid} ({name}) is missing required signatures.",
                risk="Legal enforceability risk and potential invalid contract terms.",
                recommendation="Obtain authorized signatory and vendor signatures immediately.",
                category="Missing Signatures",
                contract_id=cid,
                severity="Critical",
            ))

        if row.get("Is Expired"):
            findings.append(AuditFinding(
                finding=f"Contract {cid} expired on {row.get('End Date', 'N/A')}.",
                risk="Continued operations under expired terms may be unauthorized.",
                recommendation="Renew, terminate, or execute a new agreement without delay.",
                category="Expired Contracts",
                contract_id=cid,
                severity="Critical",
            ))

        if row.get("Auto Renew Flag") and row.get("Notice Alert"):
            findings.append(AuditFinding(
                finding=f"Auto-renew contract {cid} has an upcoming notice deadline.",
                risk="Failure to provide notice may trigger unintended renewal.",
                recommendation="Review renewal terms and submit notice if termination is desired.",
                category="Auto Renewals",
                contract_id=cid,
                severity="Warning",
            ))

        if row.get("SLA Breach"):
            target = row.get("SLA Target %", "N/A")
            actual = row.get("SLA Actual %", "N/A")
            findings.append(AuditFinding(
                finding=f"Contract {cid} SLA actual ({actual}%) is below target ({target}%).",
                risk="Service level non-compliance may trigger penalties.",
                recommendation="Engage vendor for remediation plan and monitor monthly performance.",
                category="SLA Breaches",
                contract_id=cid,
                severity="Warning",
            ))

        if row.get("Overrun Status") == "Critical":
            pct = row.get("Payment Overrun %", 0)
            findings.append(AuditFinding(
                finding=f"Contract {cid} exceeds approved contract value by {pct}%.",
                risk="Unauthorized spending and budget overruns.",
                recommendation="Review contract scope and obtain approval for excess expenditure.",
                category="Overruns",
                contract_id=cid,
                severity="Critical",
            ))
        elif row.get("Overrun Status") == "Warning":
            pct = row.get("PO Overrun %", 0)
            findings.append(AuditFinding(
                finding=f"Contract {cid} PO commitments exceed contract value by {pct}%.",
                risk="Potential budget overrun if payments follow PO commitments.",
                recommendation="Validate PO scope against contract and adjust commitments.",
                category="Overruns",
                contract_id=cid,
                severity="Warning",
            ))

        if row.get("Missing Approvals"):
            missing = []
            if row.get("Missing Legal Approval"):
                missing.append("Legal")
            if row.get("Missing Board Approval"):
                missing.append("Board")
            findings.append(AuditFinding(
                finding=f"Contract {cid} (value ${row.get('Contract Value', 0):,.0f}) missing {', '.join(missing)} approval.",
                risk="Unauthorized execution of high-value agreements.",
                recommendation="Obtain required approvals before further contract activity.",
                category="Missing Approvals",
                contract_id=cid,
                severity="Critical",
            ))

    severity_order = {"Critical": 0, "Warning": 1, "Info": 2}
    findings.sort(key=lambda f: severity_order.get(f.severity, 3))
    return findings


def findings_to_dataframe(findings: list[AuditFinding]) -> pd.DataFrame:
    if not findings:
        return pd.DataFrame(columns=["Category", "Contract ID", "Finding", "Risk", "Recommendation", "Severity"])
    return pd.DataFrame([
        {
            "Category": f.category,
            "Contract ID": f.contract_id,
            "Finding": f.finding,
            "Risk": f.risk,
            "Recommendation": f.recommendation,
            "Severity": f.severity,
        }
        for f in findings
    ])
