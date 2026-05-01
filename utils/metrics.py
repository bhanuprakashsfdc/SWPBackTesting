import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import config


def calculate_total_return(final_value: float, initial_value: float) -> float:
    if initial_value <= 0:
        return 0.0
    return ((final_value / initial_value) - 1) * 100


def calculate_cagr(final_value: float, initial_value: float, years: float) -> float:
    if initial_value <= 0 or years <= 0:
        return 0.0
    return ((final_value / initial_value) ** (1 / years) - 1) * 100


def calculate_max_drawdown(portfolio_values: pd.Series) -> float:
    if portfolio_values.empty or portfolio_values.isnull().all():
        return 0.0
    
    cummax = portfolio_values.cummax()
    drawdown = (portfolio_values - cummax) / cummax
    return drawdown.min() * 100


def calculate_sharpe(returns: pd.Series, risk_free_rate: float = 0.06) -> float:
    if returns.empty or returns.std() == 0:
        return 0.0
    
    excess_returns = returns.mean() - risk_free_rate / 12
    return (excess_returns / returns.std()) * np.sqrt(12)


def calculate_sortino(returns: pd.Series, risk_free_rate: float = 0.06) -> float:
    if returns.empty:
        return 0.0
    
    downside_returns = returns[returns < 0]
    if downside_returns.empty or downside_returns.std() == 0:
        return 0.0
    
    excess_returns = returns.mean() - risk_free_rate / 12
    return (excess_returns / downside_returns.std()) * np.sqrt(12)


def calculate_calmar(returns: pd.Series, max_drawdown: float) -> float:
    if max_drawdown >= 0:
        return 0.0
    
    annual_return = returns.mean() * 12
    return annual_return / abs(max_drawdown)


def calculate_volatility(returns: pd.Series) -> float:
    if returns.empty:
        return 0.0
    return returns.std() * np.sqrt(12) * 100


def calculate_win_rate(trades: List[Dict[str, Any]]) -> float:
    if not trades:
        return 0.0
    
    winning_trades = sum(1 for t in trades if t.get("return_pct", 0) > 0)
    return (winning_trades / len(trades)) * 100


def calculate_max_drawdown_duration(portfolio_values: pd.Series) -> int:
    if portfolio_values.empty:
        return 0
    
    cummax = portfolio_values.cummax()
    drawdown = portfolio_values - cummax
    
    in_drawdown = False
    max_duration = 0
    current_duration = 0
    
    for val in drawdown:
        if val < 0:
            in_drawdown = True
            current_duration += 1
        else:
            if in_drawdown:
                max_duration = max(max_duration, current_duration)
                current_duration = 0
            in_drawdown = False
    
    return max(max_duration, current_duration)


def calculate_rolling_returns(portfolio_values: pd.Series, windows: List[int] = [1, 3, 5]) -> Dict[str, float]:
    returns = portfolio_values.pct_change()
    results = {}
    
    for years in windows:
        months = years * 12
        if len(returns) >= months:
            rolling = returns.iloc[-months:].sum() * 100
            results[f"{years}Y"] = rolling
        else:
            results[f"{years}Y"] = 0.0
    
    return results


def calculate_all_metrics(
    portfolio: pd.DataFrame,
    initial_capital: float,
    trades: List[Dict[str, Any]],
    risk_free_rate: float = 0.06
) -> Dict[str, Any]:
    if portfolio.empty:
        return get_empty_metrics()
    
    years = len(portfolio) / 12
    final_value = portfolio.iloc[-1]["value"] if "value" in portfolio.columns else portfolio.iloc[-1]["portfolio_value"]
    
    returns = portfolio["return"].dropna() if "return" in portfolio.columns else pd.Series()
    
    max_dd = calculate_max_drawdown(
        portfolio["value"] if "value" in portfolio.columns else portfolio["portfolio_value"]
    )
    
    return {
        "initial_capital": initial_capital,
        "final_value": final_value,
        "total_return": calculate_total_return(final_value, initial_capital),
        "cagr": calculate_cagr(final_value, initial_capital, years),
        "max_drawdown": max_dd,
        "sharpe": calculate_sharpe(returns, risk_free_rate) if not returns.empty else 0.0,
        "sortino": calculate_sortino(returns, risk_free_rate) if not returns.empty else 0.0,
        "calmar": calculate_calmar(returns, max_dd) if not returns.empty else 0.0,
        "volatility": calculate_volatility(returns),
        "num_trades": len(trades),
        "win_rate": calculate_win_rate(trades),
    }


def get_empty_metrics() -> Dict[str, Any]:
    return {
        "initial_capital": 0,
        "final_value": 0,
        "total_return": 0,
        "cagr": 0,
        "max_drawdown": 0,
        "sharpe": 0,
        "sortino": 0,
        "calmar": 0,
        "volatility": 0,
        "num_trades": 0,
        "win_rate": 0,
    }


def format_metric_value(value: float, metric_type: str = "percentage") -> str:
    if metric_type == "currency":
        return f"₹{value:,.0f}"
    elif metric_type == "percentage":
        return f"{value:.2f}%"
    elif metric_type == "number":
        return f"{value:.0f}"
    else:
        return f"{value:.2f}"