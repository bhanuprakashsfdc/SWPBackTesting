from strategies.base import BaseStrategy
import pandas as pd
import numpy as np
from typing import Dict, Any, List


class ATHBreakoutStrategy(BaseStrategy):
    def __init__(self, params: Dict[str, Any]):
        super().__init__(params)
        self.confirmation_bars = params.get("confirmation_bars", 1)
        self.stop_loss = params.get("stop_loss", 0)

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        
        if "Close" not in df.columns:
            return df
        
        df["ath"] = df["Close"].cummax()
        df["above_ath"] = df["Close"] >= df["ath"]
        
        df["signal"] = 0
        
        for i in range(self.confirmation_bars, len(df)):
            if df.iloc[i]["Close"] >= df.iloc[i]["ath"]:
                if all(df.iloc[i-self.confirmation_bars:i+1]["Close"] >= df.iloc[i-self.confirmation_bars:i+1]["ath"].values):
                    df.iloc[i, df.columns.get_loc("signal")] = 1
        
        return df

    def run_backtest(self, df: pd.DataFrame) -> Dict[str, Any]:
        if df.empty:
            return self.get_empty_result()
        
        initial_capital = self.params.get("initial_capital", 100000)
        stop_loss = self.params.get("stop_loss", 0)
        
        df = self.generate_signals(df)
        
        portfolio_values = []
        current_capital = initial_capital
        position = None
        entry_price = 0
        entry_date = None
        
        for date, row in df.iterrows():
            position_value = 0
            if position is not None:
                position_value = position["shares"] * row.get("Close", 0)
            
            portfolio_total = current_capital + position_value
            
            portfolio_values.append({
                "date": date,
                "value": portfolio_total,
                "return": row.get("return", 0)
            })
            
            if position is None:
                if row.get("signal", 0) == 1 and row.get("Close", 0) > 0:
                    price = row["Close"]
                    shares = int(current_capital / price)
                    if shares > 0:
                        position = {
                            "shares": shares,
                            "entry_price": price,
                            "entry_date": date
                        }
                        current_capital -= shares * price
                        entry_price = price
                        entry_date = date
            else:
                current_price = row["Close"]
                should_exit = False
                exit_reason = ""
                
                if stop_loss > 0:
                    loss = (entry_price - current_price) / entry_price
                    if loss >= stop_loss:
                        should_exit = True
                        exit_reason = "stop_loss"
                
                if not should_exit:
                    ath = df.loc[:date, "Close"].max()
                    if current_price < ath * 0.95:
                        should_exit = True
                        exit_reason = "ath_breakdown"
                
                if should_exit:
                    current_capital += position["shares"] * current_price
                    ret_pct = (current_price - entry_price) / entry_price * 100
                    
                    self.trades.append({
                        "entry_date": entry_date,
                        "exit_date": date,
                        "symbol": "ASSET",
                        "entry_price": entry_price,
                        "exit_price": current_price,
                        "return_pct": ret_pct,
                        "exit_reason": exit_reason,
                        "holding_days": (date - entry_date).days if entry_date else 0
                    })
                    position = None
        
        if position is not None:
            final_price = df.iloc[-1]["Close"]
            current_capital += position["shares"] * final_price
        
        portfolio_df = pd.DataFrame(portfolio_values)
        portfolio_df.set_index("date", inplace=True)
        
        metrics = self._calculate_metrics(portfolio_df, initial_capital)
        
        return {
            "portfolio": portfolio_df,
            "trades": self.trades,
            "metrics": metrics
        }

    def _calculate_metrics(self, portfolio: pd.DataFrame, initial_capital: float) -> Dict[str, Any]:
        if portfolio.empty:
            return {
                "initial_capital": initial_capital,
                "final_value": 0,
                "total_return": 0,
                "cagr": 0,
                "max_drawdown": 0,
                "sharpe": 0,
                "num_trades": len(self.trades),
                "win_rate": 0,
            }
        
        final_value = portfolio.iloc[-1]["value"]
        years = len(portfolio) / 252
        
        total_return = (final_value / initial_capital - 1) * 100
        cagr = ((final_value / initial_capital) ** (1 / max(years, 0.1)) - 1) * 100
        
        cummax = portfolio["value"].cummax()
        drawdown = ((portfolio["value"] - cummax) / cummax) * 100
        drawdown = drawdown.replace([float('inf'), -100], 0)
        max_dd = drawdown.min()
        max_dd = max(-99.99, max_dd)
        
        returns = portfolio["return"].dropna()
        sharpe = (returns.mean() / returns.std() * np.sqrt(252)) if returns.std() > 0 else 0
        
        winning = sum(1 for t in self.trades if t.get("return_pct", 0) > 0)
        win_rate = (winning / len(self.trades) * 100) if self.trades else 0
        
        return {
            "initial_capital": initial_capital,
            "final_value": final_value,
            "total_return": total_return,
            "cagr": cagr,
            "max_drawdown": max_dd,
            "sharpe": sharpe,
            "num_trades": len(self.trades),
            "win_rate": win_rate,
        }