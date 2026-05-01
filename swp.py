import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="SWP Calculator",
    page_icon="📉",
    layout="wide"
)


def format_inr(value):
    if value >= 10000000:
        return f"₹{value/10000000:.2f}Cr"
    elif value >= 100000:
        return f"₹{value/100000:.2f}L"
    elif value >= 1000:
        return f"₹{value/1000:.1f}K"
    return f"₹{value:.0f}"


def run_swp(df, initial_capital, annual_withdrawal):
    annual = df.resample('YE').last()
    annual['return'] = annual['Close'].pct_change()
    annual = annual[annual['Close'].notna()]
    
    if annual.empty:
        return None
    
    portfolio = []
    value = initial_capital
    total_withdrawn = 0
    years = 0
    
    for date, row in annual.iterrows():
        if pd.isna(row['return']):
            continue
        
        pre_value = value
        value *= (1 + row['return'])
        withdrawal = min(annual_withdrawal, value)
        value -= withdrawal
        total_withdrawn += withdrawal
        years += 1
        
        portfolio.append({
            'Year': date.year,
            'Start': pre_value,
            'Return%': row['return'] * 100,
            'Before': pre_value * (1 + row['return']),
            'Withdrawn': withdrawal,
            'End': max(0, value)
        })
        
        if value <= 0:
            break
    
    df_port = pd.DataFrame(portfolio)
    
    final_value = df_port.iloc[-1]['End'] if not df_port.empty else 0
    total_return = ((final_value + total_withdrawn) / initial_capital - 1) * 100
    years_survived = len(df_port)
    cagr = ((final_value + total_withdrawn) / initial_capital) ** (1 / years_survived) - 1 if years_survived > 0 else 0
    
    return {
        'portfolio': df_port,
        'initial': initial_capital,
        'final': final_value,
        'withdrawn': total_withdrawn,
        'years': years_survived,
        'return': total_return,
        'cagr': cagr * 100
    }


st.title("📉 SWP Calculator")
st.markdown("---")

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### 📊 Input")
    initial = st.number_input("Initial Capital (₹)", value=10000000.0, step=100000.0)
    withdrawal = st.number_input("Annual Withdrawal (₹)", value=400000.0, step=10000.0)
    data_source = st.selectbox("Data", ["HDFC Balanced Advantage", "Custom CSV"])
    
    df = None
    if data_source == "HDFC Balanced Advantage":
        df = pd.read_csv("data/HDFC_Balanced_Advantage_monthly.csv", parse_dates=['Date'])
        df.set_index('Date', inplace=True)
    else:
        uploaded = st.file_uploader("Upload CSV", type=['csv'])
        if uploaded:
            df = pd.read_csv(uploaded, parse_dates=['Date'])
            df.set_index('Date', inplace=True)
    
    run_btn = st.button("Calculate SWP", type="primary")

with col2:
    if run_btn and df is not None:
        result = run_swp(df, initial, withdrawal)
        
        if result:
            st.markdown("### 📈 Results")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Initial", format_inr(result['initial']))
                st.metric("Final Value", format_inr(result['final']))
            with c2:
                st.metric("Total Return", f"{result['return']:.2f}%")
                st.metric("CAGR", f"{result['cagr']:.2f}%")
            with c3:
                st.metric("Years Survived", f"{result['years']}")
                st.metric("Total Withdrawn", format_inr(result['withdrawn']))
            
            st.markdown("### 📅 Year-by-Year")
            st.dataframe(
                result['portfolio'],
                use_container_width=True
            )
            
            st.markdown("### 📉 Portfolio Chart")
            chart_df = result['portfolio']
            st.line_chart(chart_df[['Start', 'End', 'Before']])
    else:
        st.info("Select data and click Calculate")


if __name__ == "__main__":
    st.run()