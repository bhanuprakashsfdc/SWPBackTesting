from strategies.base import BaseStrategy
import pandas as pd
import numpy as np
from typing import Dict, Any, List


class MomentumStrategy(BaseStrategy):
    def __init__(self, params: Dict[str, Any]):
        super().__init__(params)
        self.lookback = params.get("lookback", 30)
        self.max_stocks = params.get("max_stocks", 1)
        self.rebalancing = params.get("rebalancing", "monthly")

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        
        if "Close" not in df.columns:
            return df
        
        df["return"] = df["Close"].pct_change(self.lookback)
        df["signal"] = 0
        
        valid_returns = df["return"].dropna()
        if len(valid_returns) > 0:
            p80 = valid_returns.quantile(0.8)
            df.loc[df["return"] >= p80, "signal"] = 1
        
        return df

    def run_backtest(self, df: pd.DataFrame) -> Dict[str, Any]:
        if df.empty:
            return self.get_empty_result()
        
        initial_capital = self.params.get("initial_capital", 100000)
        stop_loss = self.params.get("stop_loss", 0)
        
        df = self.generate_signals(df)
        
        freq_map = {
            "daily": "D",
            "weekly": "W", 
            "monthly": "ME",
            "quarterly": "QE",
            "yearly": "YE"
        }
        rebalance_freq = freq_map.get(self.rebalancing, "ME")
        
        rebalance_idx = df.resample(rebalance_freq).first().index
        
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
                "return": row.get("return", 0) if pd.notna(row.get("return", 0)) else 0
            })
            
            if date in rebalance_idx:
                if position is None and row.get("signal", 0) == 1 and row.get("Close", 0) > 0:
                    price = row["Close"]
                    shares = int(current_capital / price)
                    if shares > 0:
                        position = {"shares": shares, "entry_price": price, "entry_date": date}
                        current_capital -= shares * price
                        entry_price = price
                        entry_date = date
                elif position is not None:
                    current_price = row["Close"]
                    exit_reason = "rebalance"
                    
                    if stop_loss > 0 and entry_price > 0:
                        loss = (entry_price - current_price) / entry_price
                        if loss >= stop_loss:
                            exit_reason = "stop_loss"
                    
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
        if not portfolio_df.empty:
            portfolio_df.set_index("date", inplace=True)
        
        metrics = self._calculate_metrics(portfolio_df, initial_capital)
        
        return {
            "portfolio": portfolio_df,
            "trades": self.trades,
            "metrics": metrics
        }

    def _calculate_metrics(self, portfolio: pd.DataFrame, initial_capital: float) -> Dict[str, Any]:
        if portfolio.empty or initial_capital <= 0:
            return {
                "initial_capital": initial_capital,
                "final_value": 0,
                "total_return": 0,
                "cagr": 0,
                "max_drawdown": 0,
                "sharpe": 0,
                "num_trades": 0,
                "win_rate": 0,
            }
        
        final_value = portfolio.iloc[-1]["value"] if "value" in portfolio.columns else initial_capital
        
        if final_value <= 0:
            total_return = -100.0
            cagr = -100.0
        else:
            total_return = ((final_value / initial_capital) - 1) * 100
            years = max(len(portfolio) / 252, 0.01)
            cagr = ((final_value / initial_capital) ** (1 / years) - 1) * 100
        
        if "value" in portfolio.columns:
            cummax = portfolio["value"].cummax()
            drawdown = ((portfolio["value"] - cummax) / cummax) * 100
            drawdown = drawdown.replace([float('inf'), -100], 0)
            max_dd = drawdown.min()
            max_dd = max(-99.99, max_dd)
        else:
            max_dd = 0
        
        returns = portfolio["return"].dropna()
        if len(returns) > 0 and returns.std() > 0:
            sharpe = (returns.mean() / returns.std()) * np.sqrt(252)
        else:
            sharpe = 0
        
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