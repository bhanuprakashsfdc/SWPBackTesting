from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple


class BaseStrategy(ABC):
    def __init__(self, params: Dict[str, Any]):
        self.params = params
        self.trades: List[Dict[str, Any]] = []
        self.portfolio_history: pd.DataFrame = None

    @abstractmethod
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        pass

    @abstractmethod
    def run_backtest(self, df: pd.DataFrame) -> Dict[str, Any]:
        pass

    def calculate_position_size(
        self,
        capital: float,
        price: float,
        stop_loss: Optional[float] = None
    ) -> int:
        if stop_loss and stop_loss > 0:
            risk_amount = capital * 0.02
            position_size = int(risk_amount / (price * stop_loss))
        else:
            position_size = int(capital / price)
        return max(1, position_size)

    def apply_stop_loss(
        self,
        entry_price: float,
        current_price: float,
        stop_loss_pct: float
    ) -> Tuple[bool, str]:
        if stop_loss_pct <= 0:
            return False, ""
        
        loss_pct = (entry_price - current_price) / entry_price
        
        if loss_pct >= stop_loss_pct:
            return True, "stop_loss"
        
        return False, ""

    def apply_take_profit(
        self,
        entry_price: float,
        current_price: float,
        take_profit_pct: float
    ) -> Tuple[bool, str]:
        if not take_profit_pct or take_profit_pct <= 0:
            return False, ""
        
        gain_pct = (current_price - entry_price) / entry_price
        
        if gain_pct >= take_profit_pct:
            return True, "take_profit"
        
        return False, ""

    def get_empty_result(self) -> Dict[str, Any]:
        return {
            "portfolio": pd.DataFrame(),
            "trades": [],
            "metrics": {
                "initial_capital": 0,
                "final_value": 0,
                "total_return": 0,
                "cagr": 0,
                "max_drawdown": 0,
                "sharpe": 0,
                "num_trades": 0,
                "win_rate": 0,
            }
        }

    def format_trade(self, trade: Dict[str, Any]) -> Dict[str, Any]:
        formatted = trade.copy()
        
        for date_col in ["entry_date", "exit_date"]:
            if date_col in formatted and pd.notna(formatted[date_col]):
                formatted[date_col] = pd.to_datetime(formatted[date_col]).strftime("%Y-%m-%d")
        
        return formatted