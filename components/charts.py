"""Plotly chart components with enterprise styling."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.config import COLORS, PLOTLY_TEMPLATE


def _apply_template(fig: go.Figure) -> go.Figure:
    fig.update_layout(**PLOTLY_TEMPLATE["layout"])
    return fig


def chart_status_distribution(df: pd.DataFrame) -> go.Figure:
    if df.empty or "Expiry Status" not in df.columns:
        fig = go.Figure()
        fig.add_annotation(text="No data available", showarrow=False)
        return _apply_template(fig)

    counts = df["Expiry Status"].value_counts().reset_index()
    counts.columns = ["Status", "Count"]
    fig = px.pie(
        counts, values="Count", names="Status",
        title="Contract Status Distribution",
        color_discrete_sequence=PLOTLY_TEMPLATE["layout"]["colorway"],
        hole=0.45,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    return _apply_template(fig)


def chart_expiry_timeline(df: pd.DataFrame) -> go.Figure:
    if df.empty or "End Date" not in df.columns:
        fig = go.Figure()
        fig.add_annotation(text="No data available", showarrow=False)
        return _apply_template(fig)

    timeline = df.groupby(df["End Date"].dt.to_period("M")).size().reset_index(name="Count")
    timeline["End Date"] = timeline["End Date"].astype(str)
    fig = px.bar(timeline, x="End Date", y="Count", title="Expiry Timeline",
                 color_discrete_sequence=[COLORS["accent"]])
    return _apply_template(fig)


def chart_auto_renew(df: pd.DataFrame) -> go.Figure:
    if df.empty or "Auto Renew Flag" not in df.columns:
        fig = go.Figure()
        fig.add_annotation(text="No data available", showarrow=False)
        return _apply_template(fig)

    counts = df["Auto Renew Flag"].map({True: "Auto-Renew Yes", False: "Auto-Renew No"}).value_counts().reset_index()
    counts.columns = ["Category", "Count"]
    fig = px.bar(counts, x="Category", y="Count", title="Auto-Renew Analysis",
                 color="Category", color_discrete_map={"Auto-Renew Yes": COLORS["warning"], "Auto-Renew No": COLORS["accent"]})
    return _apply_template(fig)


def chart_value_by_vendor(df: pd.DataFrame) -> go.Figure:
    if df.empty or "Vendor" not in df.columns:
        fig = go.Figure()
        fig.add_annotation(text="No data available", showarrow=False)
        return _apply_template(fig)

    vendor = df.groupby("Vendor")["Contract Value"].sum().reset_index().sort_values("Contract Value", ascending=True).tail(10)
    fig = px.bar(vendor, x="Contract Value", y="Vendor", orientation="h",
                 title="Contract Value by Vendor (Top 10)", color_discrete_sequence=[COLORS["accent"]])
    return _apply_template(fig)


def chart_sla_compliance(df: pd.DataFrame) -> go.Figure:
    if df.empty or "SLA Actual %" not in df.columns:
        fig = go.Figure()
        fig.add_annotation(text="No data available", showarrow=False)
        return _apply_template(fig)

    compliant = int(df["SLA Compliant"].sum()) if "SLA Compliant" in df.columns else 0
    total = len(df)
    pct = (compliant / total * 100) if total else 0

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=pct,
        title={"text": "SLA Compliance %"},
        delta={"reference": 95},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": COLORS["accent"]},
            "steps": [
                {"range": [0, 70], "color": "rgba(239,68,68,0.3)"},
                {"range": [70, 90], "color": "rgba(245,158,11,0.3)"},
                {"range": [90, 100], "color": "rgba(34,197,94,0.3)"},
            ],
            "threshold": {"line": {"color": COLORS["critical"], "width": 4}, "value": 90},
        },
    ))
    return _apply_template(fig)


def chart_approval_compliance(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", showarrow=False)
        return _apply_template(fig)

    above = df[df.get("Above Threshold", False)] if "Above Threshold" in df.columns else df
    if above.empty:
        compliant, missing = len(df), 0
    else:
        missing = int(above["Missing Approvals"].sum()) if "Missing Approvals" in above.columns else 0
        compliant = len(above) - missing

    fig = go.Figure(data=[go.Pie(
        labels=["Compliant", "Missing Approvals"],
        values=[compliant, missing],
        hole=0.5,
        marker_colors=[COLORS["success"], COLORS["critical"]],
    )])
    fig.update_layout(title="Approval Compliance %")
    return _apply_template(fig)


def chart_risk_heatmap(df: pd.DataFrame) -> go.Figure:
    if df.empty or "Risk Category" not in df.columns:
        fig = go.Figure()
        fig.add_annotation(text="No data available", showarrow=False)
        return _apply_template(fig)

    pivot = df.groupby(["Vendor", "Risk Category"]).size().unstack(fill_value=0)
    if pivot.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", showarrow=False)
        return _apply_template(fig)

    fig = px.imshow(
        pivot.values[:15],
        x=pivot.columns.tolist(),
        y=pivot.index.tolist()[:15],
        title="Contract Risk Heatmap",
        color_continuous_scale=[[0, COLORS["success"]], [0.5, COLORS["warning"]], [1, COLORS["critical"]]],
        aspect="auto",
    )
    return _apply_template(fig)


def chart_spend_vs_value(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", showarrow=False)
        return _apply_template(fig)

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Contract Value", x=df["Contract ID"], y=df["Contract Value"], marker_color=COLORS["accent"]))
    if "PO Total" in df.columns:
        fig.add_trace(go.Bar(name="PO Total", x=df["Contract ID"], y=df["PO Total"], marker_color=COLORS["warning"]))
    if "Payments Total" in df.columns:
        fig.add_trace(go.Bar(name="Payments Total", x=df["Contract ID"], y=df["Payments Total"], marker_color=COLORS["success"]))
    fig.update_layout(title="Spend vs Contract Value", barmode="group")
    return _apply_template(fig)


def chart_sla_trend(sla_df: pd.DataFrame) -> go.Figure:
    if sla_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No SLA data available", showarrow=False)
        return _apply_template(fig)

    trend = sla_df.groupby("Month").agg({"SLA Target": "mean", "SLA Actual": "mean"}).reset_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=trend["Month"], y=trend["SLA Target"], name="SLA Target", line=dict(color=COLORS["accent"])))
    fig.add_trace(go.Scatter(x=trend["Month"], y=trend["SLA Actual"], name="SLA Actual", line=dict(color=COLORS["success"])))
    fig.update_layout(title="SLA Performance Trend")
    return _apply_template(fig)


def chart_vendor_sla_scorecard(df: pd.DataFrame, sla_df: pd.DataFrame) -> go.Figure:
    if sla_df.empty:
        return chart_sla_trend(sla_df)

    vendor_map = df.set_index("Contract ID")["Vendor"].to_dict() if not df.empty else {}
    sla = sla_df.copy()
    sla["Vendor"] = sla["Contract ID"].map(vendor_map)
    vendor_sla = sla.groupby("Vendor").apply(
        lambda g: (g["SLA Actual"] >= g["SLA Target"]).mean() * 100
    ).reset_index(name="Compliance %").sort_values("Compliance %")

    fig = px.bar(vendor_sla, x="Compliance %", y="Vendor", orientation="h",
                 title="Vendor SLA Scorecard", color="Compliance %",
                 color_continuous_scale=[[0, COLORS["critical"]], [0.5, COLORS["warning"]], [1, COLORS["success"]]])
    return _apply_template(fig)
