import streamlit as st
import pandas as pd
from typing import Dict, Any

import config


def render_sidebar() -> Dict[str, Any]:
    st.sidebar.title("📉 SWP Settings")
    
    data_source = st.sidebar.radio(
        "Data Source",
        ["Upload CSV", "Preloaded Dataset", "yfinance"],
    )
    
    df = None
    data_info = {}
    
    if data_source == "Upload CSV":
        uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])
        if uploaded_file:
            from utils.data_loader import load_csv, get_data_summary
            try:
                df = pd.read_csv(uploaded_file)
                df = load_csv(uploaded_file.name)
                data_info = get_data_summary(df)
            except Exception as e:
                st.sidebar.error(f"Error: {e}")
    
    elif data_source == "Preloaded Dataset":
        from utils.data_loader import load_preloaded, get_data_summary
        dataset = st.sidebar.selectbox("Select", list(config.PRELOADED_DATASETS.keys()))
        try:
            df = load_preloaded(dataset)
            data_info = get_data_summary(df)
        except Exception as e:
            st.sidebar.error(f"Error: {e}")
    
    elif data_source == "yfinance":
        from utils.data_loader import load_yfinance, get_data_summary
        ticker = st.sidebar.text_input("Ticker", "^NSEBANK")
        start = st.sidebar.date_input("Start", pd.to_datetime("2018-01-01"))
        end = st.sidebar.date_input("End", pd.Timestamp.now().date())
        if st.sidebar.button("Load"):
            try:
                df = load_yfinance(ticker, start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
                data_info = get_data_summary(df)
                st.sidebar.success(f"Loaded {len(df)} records")
            except Exception as e:
                st.sidebar.error(f"Error: {e}")
    
    st.sidebar.divider()
    
    initial_capital = st.sidebar.number_input("Initial Capital (₹)", value=10000000.0, step=100000.0)
    
    annual_withdrawal = st.sidebar.number_input("Annual Withdrawal (₹)", value=400000.0, step=10000.0)
    
    st.sidebar.divider()
    
    dark_mode = st.sidebar.toggle("Dark Mode", value=False)
    
    params = {
        "initial_capital": initial_capital,
        "withdrawal_amount": annual_withdrawal,
        "dark_mode": dark_mode,
    }
    
    return {
        "data": df,
        "data_info": data_info,
        "params": params
    }