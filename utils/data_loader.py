import os
import pandas as pd
import numpy as np
from typing import Optional, Tuple, Dict, Any
import streamlit as st

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

import config


def load_csv(filepath: str) -> pd.DataFrame:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    df = pd.read_csv(filepath)
    df = parse_dates(df)
    return df


def parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    date_cols = [col for col in df.columns if 'date' in col.lower()]
    
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce')
    
    if 'Date' in df.columns:
        df.set_index('Date', inplace=True)
        df.sort_index(inplace=True)
    elif date_cols:
        df.set_index(date_cols[0], inplace=True)
        df.sort_index(inplace=True)
    
    df = df.infer_objects()
    return df


def validate_data(df: pd.DataFrame) -> Tuple[bool, str]:
    columns = list(df.columns) + ([df.index.name] if df.index.name else [])
    
    required = [col for col in config.REQUIRED_COLUMNS if col.lower() != 'date']
    
    has_close = any(col.lower() == 'close' for col in columns)
    if not has_close:
        return False, "Missing required column: Close"
    
    if df.empty:
        return False, "Data is empty"
    
    return True, ""


def get_data_summary(df: pd.DataFrame) -> Dict[str, Any]:
    summary = {
        "start_date": df.index.min(),
        "end_date": df.index.max(),
        "records": len(df),
        "missing_values": df.isnull().sum().sum(),
    }
    
    if "Close" in df.columns:
        summary["start_price"] = df["Close"].iloc[0]
        summary["end_price"] = df["Close"].iloc[-1]
        summary["total_return"] = (df["Close"].iloc[-1] / df["Close"].iloc[0] - 1) * 100
    
    return summary


@st.cache_data(ttl=3600)
def load_yfinance(ticker: str, start: str = "2010-01-01", end: Optional[str] = None) -> pd.DataFrame:
    if not YFINANCE_AVAILABLE:
        raise ImportError("yfinance not installed")
    
    if end is None:
        end = pd.Timestamp.now().strftime("%Y-%m-%d")
    
    df = yf.download(ticker, start=start, end=end, progress=False)
    
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    if df.empty:
        raise ValueError(f"No data found for ticker: {ticker}")
    
    df.index = pd.to_datetime(df.index)
    return df


def load_preloaded(name: str) -> pd.DataFrame:
    path = config.PRELOADED_DATASETS.get(name)
    
    if path and os.path.exists(path):
        return load_csv(path)
    
    if "niftybees" in name.lower():
        return load_yfinance("^NSEBANK")
    
    raise ValueError(f"Preloaded dataset not available: {name}")


def get_returns(df: pd.DataFrame, column: str = "Close", freq: str = "ME") -> pd.DataFrame:
    if freq == "YE":
        returns = df[column].resample("YE").last().pct_change()
    elif freq == "ME":
        returns = df[column].resample("ME").last().pct_change()
    elif freq == "D":
        returns = df[column].pct_change()
    else:
        returns = df[column].pct_change()
    
    return returns.dropna()


def resample_data(df: pd.DataFrame, freq: str = "ME") -> pd.DataFrame:
    resampled = df.resample(freq).agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum'
    })
    return resampled.dropna()


def prepare_price_data(df: pd.DataFrame, use_adj_close: bool = True) -> pd.DataFrame:
    price_col = "Adj Close" if use_adj_close and "Adj Close" in df.columns else "Close"
    
    result = pd.DataFrame({
        "Close": df[price_col]
    })
    
    if "Open" in df.columns:
        result["Open"] = df["Open"]
    if "High" in df.columns:
        result["High"] = df["High"]
    if "Low" in df.columns:
        result["Low"] = df["Low"]
    
    result = result.ffill().dropna()
    return result