"""AgGrid table helper with conditional formatting."""

import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode


def render_aggrid_table(
    df: pd.DataFrame,
    height: int = 400,
    enable_export: bool = True,
    risk_column: str = "Risk Category",
) -> None:
    """Render searchable, paginated AgGrid table."""
    if df.empty:
        st_info_no_data()
        return

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(filterable=True, sortable=True, resizable=True)
    gb.configure_pagination(enabled=True, paginationPageSize=15)
    gb.configure_grid_options(domLayout="normal")

    if risk_column in df.columns:
        cell_style = JsCode("""
        function(params) {
            if (params.value === 'Critical') {
                return {'backgroundColor': 'rgba(239,68,68,0.25)', 'color': '#FCA5A5', 'fontWeight': '600'};
            }
            if (params.value === 'High') {
                return {'backgroundColor': 'rgba(239,68,68,0.15)', 'color': '#FCA5A5'};
            }
            if (params.value === 'Medium') {
                return {'backgroundColor': 'rgba(245,158,11,0.2)', 'color': '#FCD34D'};
            }
            if (params.value === 'Low' || params.value === 'Compliant') {
                return {'backgroundColor': 'rgba(34,197,94,0.15)', 'color': '#86EFAC'};
            }
            if (params.value === 'Warning') {
                return {'backgroundColor': 'rgba(245,158,11,0.2)', 'color': '#FCD34D'};
            }
            return {};
        }
        """)
        gb.configure_column(risk_column, cellStyle=cell_style)

    if enable_export:
        gb.configure_side_bar(filters_panel=True, columns_panel=True)

    grid_options = gb.build()
    AgGrid(df, gridOptions=grid_options, height=height, theme="streamlit", allow_unsafe_jscode=True)


def st_info_no_data():
    import streamlit as st
    st.info("No data available. Upload contract data via Contract Review module.")


def format_currency_df(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    result = df.copy()
    for col in cols:
        if col in result.columns:
            result[col] = result[col].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "")
    return result
