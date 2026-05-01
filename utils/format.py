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


def format_percentage(value: float) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "0.00%"
    return f"{value:.2f}%"


def format_number(value: float) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "0"
    return f"{value:.2f}"