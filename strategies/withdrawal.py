from strategies.base import BaseStrategy
import pandas as pd
import numpy as np
from typing import Dict, Any, List
import config


class WithdrawalStrategy(BaseStrategy):
    def __init__(self, params: Dict[str, Any]):
        super().__init__(params)
        
        self.withdrawal_amount = params.get("withdrawal_amount", 0)
        self.withdrawal_freq = params.get("withdrawal_freq", "yearly")
        
        if self.withdrawal_amount and self.withdrawal_amount > 0:
            self.annual_withdrawal = self.withdrawal_amount
            self.enable_withdrawal = True
        else:
            self.annual_withdrawal = 0
            self.enable_withdrawal = False

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        
        if "Close" not in df.columns:
            return df
        
        annual = df.resample("YE").last()
        annual["return"] = annual["Close"].pct_change()
        annual["year"] = annual.index.year
        
        for idx in annual.index:
            year = idx.year
            df.loc[df.index.year == year, "return"] = annual.loc[idx, "return"]
            df.loc[df.index.year == year, "withdrawal"] = self.annual_withdrawal
        
        return df

    def run_backtest(self, df: pd.DataFrame) -> Dict[str, Any]:
        if df.empty:
            return self.get_empty_result()
        
        initial_capital = self.params.get("initial_capital", config.INITIAL_CAPITAL)
        
        if not self.enable_withdrawal or self.annual_withdrawal <= 0:
            return self._run_without_withdrawal(df, initial_capital)
        
        df = self.generate_signals(df)
        
        annual_data = df.resample("YE").last()
        annual_data = annual_data[annual_data["Close"].notna()]
        
        if annual_data.empty:
            return self.get_empty_result()
        
        portfolio_values = []
        current_value = initial_capital
        years_survived = 0
        total_withdrawn = 0
        
        for idx, row in annual_data.iterrows():
            year = int(row.name.year)
            annual_return = row.get("return", 0)
            
            if pd.isna(annual_return):
                continue
            
            current_value *= (1 + annual_return)
            
            withdrawal = min(self.annual_withdrawal, current_value)
            current_value -= withdrawal
            
            portfolio_values.append({
                "date": idx,
                "year": year,
                "pre_withdrawal_value": current_value + withdrawal,
                "withdrawal": withdrawal,
                "post_withdrawal_value": max(0, current_value),
                "annual_return": annual_return * 100
            })
            
            total_withdrawn += withdrawal
            years_survived += 1
            
            if current_value <= 0:
                current_value = 0
                break
        
        portfolio_df = pd.DataFrame(portfolio_values)
        if not portfolio_df.empty:
            portfolio_df.set_index("date", inplace=True)
        
        metrics = self._calculate_metrics(portfolio_df, initial_capital, years_survived, total_withdrawn)
        
        return {
            "portfolio": portfolio_df,
            "trades": self.trades,
            "metrics": metrics
        }

    def _run_without_withdrawal(self, df: pd.DataFrame, initial_capital: float) -> Dict[str, Any]:
        df = self.generate_signals(df)
        annual_data = df.resample("YE").last()
        annual_data = annual_data[annual_data["Close"].notna()]
        
        if annual_data.empty:
            return self.get_empty_result()
        
        portfolio_values = []
        current_value = initial_capital
        
        for idx, row in annual_data.iterrows():
            year = int(row.name.year)
            annual_return = row.get("return", 0)
            
            if pd.isna(annual_return):
                continue
            
            current_value *= (1 + annual_return)
            
            portfolio_values.append({
                "date": idx,
                "year": year,
                "pre_withdrawal_value": 0,
                "withdrawal": 0,
                "post_withdrawal_value": current_value,
                "annual_return": annual_return * 100
            })
        
        portfolio_df = pd.DataFrame(portfolio_values)
        if not portfolio_df.empty:
            portfolio_df.set_index("date", inplace=True)
        
        final_value = portfolio_df.iloc[-1]["post_withdrawal_value"] if not portfolio_df.empty else initial_capital
        years = len(portfolio_df)
        total_return = (final_value / initial_capital - 1) * 100
        cagr = ((final_value / initial_capital) ** (1 / years) - 1) * 100 if years > 0 else 0
        
        return {
            "portfolio": portfolio_df,
            "trades": [],
            "metrics": {
                "initial_capital": initial_capital,
                "final_value": final_value,
                "total_return": total_return,
                "cagr": cagr,
                "cagr_before": portfolio_df["annual_return"].mean() if not portfolio_df.empty else 0,
                "max_drawdown": 0,
                "sharpe": 0,
                "num_trades": years,
                "win_rate": 100,
                "total_withdrawn": 0,
                "years_survived": years,
            }
        }

    def _calculate_metrics(
        self,
        portfolio: pd.DataFrame,
        initial_capital: float,
        years_survived: int,
        total_withdrawn: float
    ) -> Dict[str, Any]:
        if portfolio.empty:
            return {
                "initial_capital": initial_capital,
                "final_value": 0,
                "total_return": 0,
                "cagr": 0,
                "cagr_before": 0,
                "max_drawdown": 0,
                "sharpe": 0,
                "num_trades": years_survived,
                "win_rate": 0,
                "total_withdrawn": 0,
                "years_survived": 0,
            }
        
        final_value = portfolio.iloc[-1]["post_withdrawal_value"]
        
        total_return = ((final_value + total_withdrawn) / initial_capital - 1) * 100
        cagr_before = portfolio["annual_return"].mean()
        
        total_value = final_value + total_withdrawn
        cagr_after = ((total_value / initial_capital) ** (1 / max(years_survived, 1)) - 1) * 100
        
        if "post_withdrawal_value" in portfolio.columns:
            cummax = portfolio["post_withdrawal_value"].cummax()
            drawdown = ((portfolio["post_withdrawal_value"] - cummax) / cummax) * 100
            drawdown = drawdown.replace([float('inf'), -100], 0)
            max_dd = drawdown.min()
            max_dd = max(-99.99, max_dd)
        else:
            max_dd = 0
        
        returns = portfolio["annual_return"].dropna()
        sharpe = (returns.mean() / returns.std()) if returns.std() > 0 else 0
        
        return {
            "initial_capital": initial_capital,
            "final_value": final_value,
            "total_return": total_return,
            "cagr": cagr_after,
            "cagr_before": cagr_before,
            "max_drawdown": max_dd,
            "sharpe": sharpe,
            "num_trades": years_survived,
            "win_rate": 100,
            "total_withdrawn": total_withdrawn,
            "years_survived": years_survived,
        }