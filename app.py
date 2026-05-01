import streamlit as st
import pandas as pd
from typing import Dict, Any

from components.sidebar import render_sidebar
from components.metrics_display import render_data_summary
from utils.plotting import plot_equity_curve
from strategies.withdrawal import WithdrawalStrategy

st.set_page_config(
    page_title="SWP Calculator",
    page_icon="📉",
    layout="wide",
    initial_sidebar_state="expanded"
)


def init_session_state():
    if "results" not in st.session_state:
        st.session_state.results = None


def run_backtest(df: pd.DataFrame, params: Dict[str, Any]):
    strategy = WithdrawalStrategy(params)
    return strategy.run_backtest(df)


def main():
    init_session_state()
    
    st.title("📉 SWP Calculator")
    st.markdown("---")
    
    sidebar_data = render_sidebar()
    
    df = sidebar_data.get("data")
    data_info = sidebar_data.get("data_info", {})
    params = sidebar_data.get("params", {})
    dark_mode = params.get("dark_mode", False)
    
    if df is not None and not df.empty:
        render_data_summary(data_info)
        
        st.markdown("---")
        
        if st.button("Calculate SWP", type="primary", use_container_width=True):
            with st.spinner("Calculating..."):
                try:
                    results = run_backtest(df, params)
                    st.session_state.results = results
                except Exception as e:
                    st.error(f"Error: {e}")
        
        if st.session_state.results:
            results = st.session_state.results
            metrics = results["metrics"]
            portfolio = results["portfolio"]
            
            st.markdown("---")
            st.markdown("### Results")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Initial", f"₹{metrics['initial_capital']/10000000:.2f}Cr")
            with col2:
                st.metric("Withdrawn", f"₹{metrics['total_withdrawn']/10000000:.2f}Cr")
            with col3:
                st.metric("Years", f"{metrics['years_survived']}")
            
            col4, col5, col6 = st.columns(3)
            with col4:
                st.metric("Final", f"₹{metrics['final_value']/10000000:.2f}Cr")
            with col5:
                st.metric("Return", f"{metrics['total_return']:.2f}%")
            with col6:
                st.metric("CAGR", f"{metrics['cagr']:.2f}%")
            
            st.markdown("---")
            st.markdown("### Year-by-Year")
            
            if not portfolio.empty:
                st.dataframe(portfolio, use_container_width=True)


if __name__ == "__main__":
    main()