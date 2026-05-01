import streamlit as st
from typing import Dict, Any, Optional
import pandas as pd


def format_inr_crore(value: float) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "₹0"
    
    abs_value = abs(value)
    
    if abs_value >= 10000000:
        return f"₹{value/10000000:.2f}Cr"
    elif abs_value >= 100000:
        return f"₹{value/100000:.2f}L"
    elif abs_value >= 1000:
        return f"₹{value/1000:.2f}K"
    else:
        return f"₹{value:.0f}"


def format_inr_full(value: float) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "₹0"
    return f"₹{value:,.0f}"


def format_pct(value: float) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "0%"
    return f"{value:.2f}%"


def render_metric_card(label: str, value: Any, delta: Optional[float] = None, help_text: Optional[str] = None):
    st.metric(label=label, value=value, delta=delta, help=help_text)


def render_metrics_grid(metrics: Dict[str, Any]):
    col1, col2, col3 = st.columns(3)
    
    total_ret = metrics.get('total_return', 0)
    cagr = metrics.get('cagr', 0)
    max_dd = metrics.get('max_drawdown', 0)
    
    if max_dd < -50:
        max_dd_display = f"{max_dd:.0f}%"
    else:
        max_dd_display = f"{max_dd:.2f}%"
    
    with col1:
        render_metric_card("Total Return", format_pct(total_ret))
        render_metric_card("CAGR", format_pct(cagr))
        render_metric_card("Max Drawdown", max_dd_display, delta=max_dd)
    
    with col2:
        render_metric_card("Sharpe Ratio", f"{metrics.get('sharpe', 0):.2f}")
        render_metric_card("Sortino Ratio", f"{metrics.get('sortino', 0):.2f}")
        render_metric_card("Calmar Ratio", f"{metrics.get('calmar', 0):.2f}")
    
    with col3:
        render_metric_card("Win Rate", format_pct(metrics.get('win_rate', 0)))
        render_metric_card("Total Trades", f"{metrics.get('num_trades', 0)}")
        render_metric_card("Final Value", format_inr_crore(metrics.get('final_value', 0)))


def render_risk_metrics(metrics: Dict[str, Any]):
    st.subheader("📊 Risk Metrics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Volatility", format_pct(metrics.get('volatility', 0)))
    with col2:
        st.metric("Beta", f"{metrics.get('beta', 0):.2f}")
    with col3:
        st.metric("Alpha", format_pct(metrics.get('alpha', 0)))
    with col4:
        st.metric("Max Drawdown", format_pct(max(-99.99, metrics.get('max_drawdown', 0))))


def render_data_summary(data_info: Dict[str, Any]):
    if not data_info:
        return
    st.subheader("📈 Data Summary")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Records", f"{data_info.get('records', 0):,}")
    with col2:
        sd = data_info.get('start_date')
        st.metric("Start Date", sd.strftime("%Y-%m-%d") if sd else "-")
    with col3:
        ed = data_info.get('end_date')
        st.metric("End Date", ed.strftime("%Y-%m-%d") if ed else "-")
    with col4:
        st.metric("Missing", f"{data_info.get('missing_values', 0)}")