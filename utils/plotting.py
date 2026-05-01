import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Optional, List, Dict
import config


def hex_to_rgba(hex_color: str, alpha: float = 1.0) -> str:
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


LIGHT_COLORS = {
    "primary": "#1f77b4",
    "success": "#28a745",
    "danger": "#dc3545",
    "warning": "#ffc107",
    "background": "#ffffff",
    "grid": "#e0e0e0",
    "text": "#262730",
    "primary_alpha": "rgba(31,119,180,0.2)",
    "danger_alpha": "rgba(220,53,69,0.3)",
}

DARK_COLORS = {
    "primary": "#4da6ff",
    "success": "#3cb371",
    "danger": "#ff6b6b",
    "warning": "#ffd93d",
    "background": "#0e1117",
    "grid": "#333333",
    "text": "#fafafa",
    "primary_alpha": "rgba(77,166,255,0.2)",
    "danger_alpha": "rgba(255,107,107,0.3)",
}


def get_colors(dark_mode: bool = False) -> dict:
    return DARK_COLORS if dark_mode else LIGHT_COLORS


def plot_equity_curve(
    portfolio: pd.DataFrame,
    benchmark: Optional[pd.DataFrame] = None,
    dark_mode: bool = False,
    title: str = "Portfolio Value"
) -> go.Figure:
    colors = get_colors(dark_mode)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=portfolio.index,
        y=portfolio["value"] if "value" in portfolio.columns else portfolio["portfolio_value"],
        mode="lines",
        name="Portfolio",
        line=dict(color=colors["primary"], width=2),
        fill="tozeroy",
        fillcolor=colors["primary_alpha"]
    ))
    
    if benchmark is not None and not benchmark.empty:
        fig.add_trace(go.Scatter(
            x=benchmark.index,
            y=benchmark,
            mode="lines",
            name="Benchmark",
            line=dict(color=colors["text"], width=1.5, dash="dash")
        ))
    
    fig.update_layout(
        title=dict(text=title, x=0.5),
        xaxis_title="Date",
        yaxis_title="Value (₹)",
        template="plotly_dark" if dark_mode else "plotly",
        paper_bgcolor=colors["background"],
        plot_bgcolor=colors["background"],
        font=dict(color=colors["text"]),
        hovermode="x unified",
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        margin=dict(l=60, r=20, t=60, b=40)
    )
    
    fig.update_xaxes(showgrid=True, gridcolor=colors["grid"])
    fig.update_yaxes(showgrid=True, gridcolor=colors["grid"])
    
    return fig


def plot_drawdown(
    portfolio_values: pd.Series,
    dark_mode: bool = False,
    title: str = "Drawdown"
) -> go.Figure:
    colors = get_colors(dark_mode)
    
    cummax = portfolio_values.cummax()
    drawdown = ((portfolio_values - cummax) / cummax) * 100
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=drawdown.index,
        y=drawdown,
        mode="lines",
        name="Drawdown",
        line=dict(color=colors["danger"], width=2),
        fill="tozeroy",
        fillcolor=colors["danger_alpha"]
    ))
    
    fig.update_layout(
        title=dict(text=title, x=0.5),
        xaxis_title="Date",
        yaxis_title="Drawdown (%)",
        template="plotly_dark" if dark_mode else "plotly",
        paper_bgcolor=colors["background"],
        plot_bgcolor=colors["background"],
        font=dict(color=colors["text"]),
        hovermode="x unified",
        margin=dict(l=60, r=20, t=60, b=40)
    )
    
    fig.update_xaxes(showgrid=True, gridcolor=colors["grid"])
    fig.update_yaxes(showgrid=True, gridcolor=colors["grid"])
    
    return fig


def plot_monthly_heatmap(
    returns: pd.Series,
    dark_mode: bool = False,
    title: str = "Monthly Returns"
) -> go.Figure:
    colors = get_colors(dark_mode)
    
    if returns.empty:
        return go.Figure()
    
    df = returns.to_frame("return")
    df["year"] = df.index.year
    df["month"] = df.index.month
    
    pivot = df.pivot_table(values="return", index="year", columns="month", aggfunc="sum") * 100
    
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    pivot.columns = [months[i-1] for i in pivot.columns]
    
    fig = go.Figure()
    
    colorscale = [
        [0, colors["danger"]],
        [0.5, colors["background"]],
        [1, colors["success"]]
    ]
    
    fig.add_trace(go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale=colorscale,
        zmid=0,
        text=pivot.values,
        texttemplate="%{z:.1f}%",
        textfont=dict(size=10),
        hovertemplate="Month: %{x}<br>Year: %{y}<br>Return: %{z:.2f}%<extra></extra>"
    ))
    
    fig.update_layout(
        title=dict(text=title, x=0.5),
        xaxis_title="Month",
        yaxis_title="Year",
        template="plotly_dark" if dark_mode else "plotly",
        paper_bgcolor=colors["background"],
        plot_bgcolor=colors["background"],
        font=dict(color=colors["text"]),
        margin=dict(l=60, r=20, t=60, b=40)
    )
    
    return fig


def plot_trade_histogram(
    trades: List[Dict],
    dark_mode: bool = False,
    title: str = "Trade Returns Distribution"
) -> go.Figure:
    colors = get_colors(dark_mode)
    
    if not trades:
        return go.Figure()
    
    returns = [t.get("return_pct", 0) for t in trades]
    
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=returns,
        nbinsx=20,
        marker_color=colors["primary"],
        opacity=0.75
    ))
    
    fig.add_vline(x=0, line_dash="dash", line_color=colors["danger"])
    
    fig.update_layout(
        title=dict(text=title, x=0.5),
        xaxis_title="Return (%)",
        yaxis_title="Count",
        template="plotly_dark" if dark_mode else "plotly",
        paper_bgcolor=colors["background"],
        plot_bgcolor=colors["background"],
        font=dict(color=colors["text"]),
        margin=dict(l=60, r=20, t=60, b=40)
    )
    
    fig.update_xaxes(showgrid=True, gridcolor=colors["grid"])
    fig.update_yaxes(showgrid=True, gridcolor=colors["grid"])
    
    return fig


def plot_benchmark_comparison(
    portfolio: pd.DataFrame,
    benchmark: pd.DataFrame,
    dark_mode: bool = False,
    title: str = "Portfolio vs Benchmark"
) -> go.Figure:
    colors = get_colors(dark_mode)
    
    port_values = portfolio["value"] if "value" in portfolio.columns else portfolio["portfolio_value"]
    port_norm = (port_values / port_values.iloc[0]) * 100
    bench_norm = (benchmark / benchmark.iloc[0]) * 100
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=port_norm.index,
        y=port_norm,
        mode="lines",
        name="Portfolio",
        line=dict(color=colors["primary"], width=2)
    ))
    fig.add_trace(go.Scatter(
        x=bench_norm.index,
        y=bench_norm,
        mode="lines",
        name="Benchmark",
        line=dict(color=colors["text"], width=2, dash="dash")
    ))
    
    fig.update_layout(
        title=dict(text=title, x=0.5),
        xaxis_title="Date",
        yaxis_title="Normalized Value (100 = Base)",
        template="plotly_dark" if dark_mode else "plotly",
        paper_bgcolor=colors["background"],
        plot_bgcolor=colors["background"],
        font=dict(color=colors["text"]),
        hovermode="x unified",
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        margin=dict(l=60, r=20, t=60, b=40)
    )
    
    fig.update_xaxes(showgrid=True, gridcolor=colors["grid"])
    fig.update_yaxes(showgrid=True, gridcolor=colors["grid"])
    
    return fig


def plot_monte_carlo(
    simulations: pd.DataFrame,
    dark_mode: bool = False,
    title: str = "Monte Carlo Projections"
) -> go.Figure:
    colors = get_colors(dark_mode)
    
    percentiles = [10, 25, 50, 75, 90]
    
    fig = go.Figure()
    
    for pct in percentiles:
        label = f"P{pct}"
        color = colors["primary"] if pct == 50 else colors["text"]
        opacity = 0.3 if pct not in [10, 90] else 0.15
        
        fig.add_trace(go.Scatter(
            x=simulations.index,
            y=simulations[str(pct)],
            mode="lines",
            name=label,
            line=dict(color=color, width=1, dash="dash" if pct not in [10, 90] else "dot"),
            opacity=opacity
        ))
    
    fig.update_layout(
        title=dict(text=title, x=0.5),
        xaxis_title="Days",
        yaxis_title="Portfolio Value (₹)",
        template="plotly_dark" if dark_mode else "plotly",
        paper_bgcolor=colors["background"],
        plot_bgcolor=colors["background"],
        font=dict(color=colors["text"]),
        hovermode="x unified",
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        margin=dict(l=60, r=20, t=60, b=40)
    )
    
    return fig


def plot_sector_allocation(
    holdings: Dict[str, float],
    dark_mode: bool = False,
    title: str = "Sector Allocation"
) -> go.Figure:
    colors = get_colors(dark_mode)
    
    sectors = list(holdings.keys())
    values = list(holdings.values())
    
    fig = go.Figure(data=[go.Pie(
        labels=sectors,
        values=values,
        hole=0.4,
        marker=dict(colors=[
            config.COLORS["primary"],
            config.COLORS["success"],
            config.COLORS["warning"],
            config.COLORS["danger"],
            "#9370db",
            "#20b2aa",
            "#ff8c00"
        ])
    )])
    
    fig.update_layout(
        title=dict(text=title, x=0.5),
        template="plotly_dark" if dark_mode else "plotly",
        paper_bgcolor=colors["background"],
        font=dict(color=colors["text"]),
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig


def export_to_image(fig: go.Figure, format: str = "png") -> bytes:
    return fig.to_image(format=format, scale=2)