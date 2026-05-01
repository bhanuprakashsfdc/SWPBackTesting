import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Optional


def render_trade_log(
    trades: List[Dict[str, Any]],
    show_download: bool = True,
    key: str = "trade_log"
) -> None:
    if not trades:
        st.info("No trades to display")
        return
    
    df = pd.DataFrame(trades)
    
    if "entry_date" in df.columns:
        df["entry_date"] = pd.to_datetime(df["entry_date"]).dt.strftime("%Y-%m-%d")
    if "exit_date" in df.columns:
        df["exit_date"] = pd.to_datetime(df["exit_date"]).dt.strftime("%Y-%m-%d")
    if "return_pct" in df.columns:
        df["return_pct"] = df["return_pct"].apply(lambda x: f"{x:.2f}%")
    if "entry_price" in df.columns:
        df["entry_price"] = df["entry_price"].apply(lambda x: f"₹{x:.2f}")
    if "exit_price" in df.columns:
        df["exit_price"] = df["exit_price"].apply(lambda x: f"₹{x:.2f}")
    
    column_config = {}
    if "return_pct" in df.columns:
        column_config["return_pct"] = st.column_config.TextColumn(
            "Return",
            help="Trade return percentage"
        )
    
    st.dataframe(
        df,
        use_container_width=True,
        column_config=column_config,
        hide_index=True
    )
    
    if show_download:
        csv = df.to_csv(index=False).encode("utf-8")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.download_button(
                "📥 Download Trade Log (CSV)",
                data=csv,
                file_name="trade_log.csv",
                mime="text/csv",
                key=f"{key}_download"
            )
        
        with col2:
            winning = sum(1 for t in trades if t.get("return_pct", 0) > 0)
            losing = len(trades) - winning
            st.metric("Winning Trades", f"{winning}/{len(trades)}")


def render_trade_stats(trades: List[Dict[str, Any]]) -> None:
    if not trades:
        return
    
    winning = sum(1 for t in trades if t.get("return_pct", 0) > 0)
    losing = sum(1 for t in trades if t.get("return_pct", 0) <= 0)
    
    avg_win = sum(t.get("return_pct", 0) for t in trades if t.get("return_pct", 0) > 0)
    avg_win = avg_win / winning if winning > 0 else 0
    
    avg_loss = sum(t.get("return_pct", 0) for t in trades if t.get("return_pct", 0) <= 0)
    avg_loss = avg_loss / losing if losing > 0 else 0
    
    profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Trades", len(trades))
    with col2:
        st.metric("Win Rate", f"{(winning/len(trades)*100):.1f}%")
    with col3:
        st.metric("Avg Win", f"{avg_win:.2f}%")
    with col4:
        st.metric("Avg Loss", f"{avg_loss:.2f}%")
    
    col5, col6 = st.columns(2)
    with col5:
        st.metric("Profit Factor", f"{profit_factor:.2f}")
    with col6:
        holding_periods = [t.get("holding_days", 0) for t in trades if "holding_days" in t]
        avg_holding = sum(holding_periods) / len(holding_periods) if holding_periods else 0
        st.metric("Avg Holding Period", f"{avg_holding:.0f} days")


def filter_trades(
    trades: List[Dict[str, Any]],
    min_return: Optional[float] = None,
    max_return: Optional[float] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[Dict[str, Any]]:
    filtered = trades
    
    if min_return is not None:
        filtered = [t for t in filtered if t.get("return_pct", 0) >= min_return]
    
    if max_return is not None:
        filtered = [t for t in filtered if t.get("return_pct", 0) <= max_return]
    
    if start_date:
        filtered = [t for t in filtered if t.get("entry_date", "") >= start_date]
    
    if end_date:
        filtered = [t for t in filtered if t.get("entry_date", "") <= end_date]
    
    return filtered