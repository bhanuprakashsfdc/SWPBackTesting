import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Optional


@dataclass
class BacktestConfig:
    initial_capital: float = 1_00_00_000
    annual_withdrawal: float = 4_00_000
    price_col: str = "Close"


class PortfolioBacktester:
    def __init__(self, config: BacktestConfig):
        self.config = config
        self.results = None
        self.portfolio_history = None

    def load_data(self, filepath: str) -> pd.DataFrame:
        df = pd.read_csv(filepath, parse_dates=["Date"])
        df.set_index("Date", inplace=True)
        df.sort_index(inplace=True)
        return df

    def compute_annual_returns(self, df: pd.DataFrame) -> pd.DataFrame:
        annual = df.resample("YE").last()
        annual["Return"] = annual[self.config.price_col].pct_change()
        annual["Year"] = annual.index.year
        return annual.dropna(subset=["Return"]).reset_index()

    def run(self, df: pd.DataFrame) -> dict:
        annual_data = self.compute_annual_returns(df)
        if annual_data.empty:
            raise ValueError("No annual data available")

        portfolio_values = []
        withdrawals = []
        years_survived = 0
        total_withdrawn = 0
        current_value = self.config.initial_capital

        initial_value = current_value

        for _, row in annual_data.iterrows():
            year = int(row["Year"])
            annual_return = row["Return"]

            current_value *= (1 + annual_return)

            withdrawal = min(self.config.annual_withdrawal, current_value)
            current_value -= withdrawal

            portfolio_values.append({
                "Year": year,
                "Pre_Withdrawal_Value": current_value + withdrawal,
                "Withdrawal": withdrawal,
                "Post_Withdrawal_Value": max(0, current_value),
                "Annual_Return": annual_return
            })
            withdrawals.append(withdrawal)
            total_withdrawn += withdrawal
            years_survived += 1

            if current_value <= 0:
                current_value = 0
                break

        portfolio_df = pd.DataFrame(portfolio_values)
        self.portfolio_history = portfolio_df.copy()

        final_value = portfolio_df.iloc[-1]["Post_Withdrawal_Value"] if not portfolio_df.empty else 0

        returns = portfolio_df["Annual_Return"].dropna()
        cagr_before = (1 + returns.mean()) - 1
        cagr_after = ((final_value / self.config.initial_capital) ** (1 / years_survived) - 1) if years_survived > 0 else 0

        running_max = portfolio_df["Post_Withdrawal_Value"].cummax()
        drawdown = (portfolio_df["Post_Withdrawal_Value"] - running_max) / running_max
        max_drawdown = drawdown.min()

        self.results = {
            "Year_wise_Portfolio": portfolio_df.to_dict("records"),
            "Total_Withdrawals": total_withdrawn,
            "Final_Portfolio_Value": final_value,
            "Years_Survived": years_survived,
            "CAGR_Before_Withdrawals": cagr_before,
            "CAGR_After_Withdrawals": cagr_after,
            "Max_Drawdown": max_drawdown,
            "Initial_Capital": self.config.initial_capital
        }
        return self.results

    def plot(self, title: str = "Portfolio Withdrawal Backtest"):
        if self.portfolio_history is None:
            raise ValueError("Run backtest first")

        df = self.portfolio_history
        years = df["Year"]
        post_values = df["Post_Withdrawal_Value"]

        plt.figure(figsize=(12, 6))
        plt.plot(years, post_values, marker="o", linewidth=2, label="Portfolio Value")
        plt.scatter(df["Year"], df["Post_Withdrawal_Value"], s=100, c="red", zorder=5, label="Withdrawal Points")

        for i, row in df.iterrows():
            plt.annotate(
                f"₹{row['Post_Withdrawal_Value']/1e6:.2f}M",
                (row["Year"], row["Post_Withdrawal_Value"]),
                textcoords="offset points", xytext=(0, 10), ha="center", fontsize=8
            )

        plt.axhline(y=self.config.initial_capital, color="gray", linestyle="--", alpha=0.5, label="Initial Capital")
        plt.xlabel("Year")
        plt.ylabel("Portfolio Value (INR)")
        plt.title(title)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()

    def print_summary(self):
        if self.results is None:
            raise ValueError("Run backtest first")

        r = self.results
        print("\n" + "=" * 50)
        print("PORTFOLIO WITHDRAWAL BACKTEST SUMMARY")
        print("=" * 50)
        print(f"Initial Capital:           ₹{r['Initial_Capital']:,.0f}")
        print(f"Annual Withdrawal:         ₹{self.config.annual_withdrawal:,.0f}")
        print(f"Total Withdrawals:         ₹{r['Total_Withdrawals']:,.0f}")
        print(f"Final Portfolio Value:    ₹{r['Final_Portfolio_Value']:,.0f}")
        print(f"Years Survived:            {r['Years_Survived']}")
        print(f"CAGR (Before Withdrawals): {r['CAGR_Before_Withdrawals']*100:.2f}%")
        print(f"CAGR (After Withdrawals):   {r['CAGR_After_Withdrawals']*100:.2f}%")
        print(f"Maximum Drawdown:          {r['Max_Drawdown']*100:.2f}%")
        print("=" * 50)
        print("\nYear-wise Portfolio Value:")
        print("-" * 70)
        print(f"{'Year':<8}{'Pre-Value':<15}{'Withdrawal':<15}{'Post-Value':<15}")
        print("-" * 70)
        for row in r["Year_wise_Portfolio"]:
            print(f"{int(row['Year']):<8}₹{row['Pre_Withdrawal_Value']/1e6:<14.2f}M₹{row['Withdrawal']/1e6:<14.2f}M₹{row['Post_Withdrawal_Value']/1e6:<14.2f}M")
        print("-" * 70)


if __name__ == "__main__":
    config = BacktestConfig(
        initial_capital=1_00_00_000,
        annual_withdrawal=4_00_000
    )

    backtester = PortfolioBacktester(config)
    df = backtester.load_data("data/HDFC_Balanced_Advantage_monthly.csv")

    results = backtester.run(df)
    backtester.print_summary()
    backtester.plot("HDFC Balanced Advantage - Withdrawal Strategy")