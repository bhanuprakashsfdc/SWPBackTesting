# Trading Strategy Dashboard - Implementation Plan

## Overview
A 3-phase implementation plan to build a professional trading dashboard with backtesting capabilities.

---

## Phase 1: Core Infrastructure (Priority: HIGH)

### 1.1 Setup & Config
**Files**: `config.py`, `requirements.txt`

**config.py**:
- Default constants (INITIAL_CAPITAL, DEFAULT_EMA, etc.)
- Preloaded datasets dictionary
- Color palette definitions
- Theme settings

**requirements.txt**:
```
streamlit
pandas
numpy
plotly
matplotlib
yfinance
```

### 1.2 Data Loading
**Files**: `utils/data_loader.py`, `utils/__init__.py`

**data_loader.py**:
- `load_csv(filepath)` - Load and parse CSV
- `get_preloaded(name)` - Get preloaded dataset
- `validate_data(df)` - Check required columns
- `get_data_summary(df)` - Return statistics
- yfinance integration functions

### 1.3 Base Strategy
**Files**: `strategies/base.py`, `strategies/__init__.py`

**base.py**:
- `BaseStrategy` - Abstract class
- `generate_signals(df, params)` - Generate trading signals
- `calculate_portfolio(df, signals, capital)` - Simulate trades
- Methods: entry, exit, position sizing

### 1.4 Metrics Utility
**Files**: `utils/metrics.py`, `utils/__init__.py`

**metrics.py**:
- `calculate_returns(portfolio)` - Total returns
- `calculate_cagr(portfolio, years)` - CAGR
- `calculate_max_drawdown(portfolio)` - Max drawdown
- `calculate_sharpe(portfolio)` - Sharpe ratio
- `calculate_win_rate(trades)` - Win rate

### 1.5 Main App
**Files**: `app.py` (Phase 1 version)

**app.py**:
- Streamlit page config
- Session state initialization
- Basic sidebar structure
- Overview tab with metrics
- Data loading and display
- Simple backtest execution

### Phase 1 Deliverables
- [ ] Working Streamlit app
- [ ] CSV upload and display
- [ ] Basic portfolio backtest
- [ ] Core metrics in cards
- [ ] Simple equity chart

---

## Phase 2: Features & Visualization

### 2.1 Strategy Implementations
**Files**: `strategies/momentum.py`, `strategies/ath_breakout.py`, `strategies/moving_average.py`, `strategies/withdrawal.py`

**momentum.py**:
- Rank stocks by lookback return
- Hold top N performers
- Rebalancing logic

**ath_breakout.py**:
- Track all-time high
- Confirmation bars logic
- Entry/exit signals

**moving_average.py**:
- Fast/Slow EMA calculation
- Crossover detection
- Signal generation

**withdrawal.py** (extend from backtest.py):
- Fixed withdrawal logic
- Annual return calculation
- Survival tracking

### 2.2 Plotting Utilities
**Files**: `utils/plotting.py`, `utils/__init__.py`

**plotting.py**:
- `plot_equity_curve(portfolio, benchmark)` - Line chart
- `plot_drawdown(portfolio)` - Area chart
- `plot_monthly_heatmap(returns)` - Heatmap
- `plot_trade_histogram(trades)` - Bar chart
- `plot_benchmark(portfolio, benchmark)` - Comparison

### 2.3 Components
**Files**: `components/sidebar.py`, `components/tabs.py`, `components/metrics_display.py`

**sidebar.py**:
- File uploader widget
- Strategy dropdown
- Parameter inputs (sliders, number inputs)
- Theme toggle

**tabs.py**:
- Tab content handlers
- Navigation logic

**metrics_display.py**:
- Metric card components
- Delta formatting

### 2.4 Trade Log
**Files**: `components/trade_log.py`

**trade_log.py**:
- Trade table display
- Sorting and filtering
- CSV download button

### 2.5 Dark Mode
**Implementation**:
- Session state for theme
- Streamlit theme config
- Chart color updates for dark mode

### Phase 2 Deliverables
- [ ] All 4 strategies implemented
- [ ] Full sidebar with parameters
- [ ] Interactive charts (Plotly)
- [ ] Drawdown chart
- [ ] Trade log table
- [ ] Monthly heatmap
- [ ] Dark mode toggle

---

## Phase 3: Advanced Analytics

### 3.1 Risk Metrics
**Files**: `utils/metrics.py` (extend)

**Additions**:
- `calculate_sortino(portfolio)` - Sortino ratio
- `calculate_calmar(portfolio)` - Calmar ratio
- `calculate_volatility(portfolio)` - Annual vol
- `calculate_beta(portfolio, benchmark)` - Beta

### 3.2 Analytics Tab
**Files**: `components/tabs.py` (extend)

**Features**:
- Rolling returns (1Y, 3Y, 5Y)
- Risk metrics display
- Scenario analysis

### 3.3 Monte Carlo
**Files**: `utils/metrics.py` (extend)

**monte_carlo.py**:
- `run_monte_carlo(portfolio, n=1000)` - Simulations
- `plot_simulations(simulations)` - Cone chart
- Confidence intervals

### 3.4 yfinance Integration
**Files**: `utils/data_loader.py` (extend)

**Additions**:
- Ticker input field
- Live data download
- Batch download for portfolios

### 3.5 Export Functionality
**Files**: `components/trade_log.py`, `utils/plotting.py`

**Features**:
- Download results as CSV
- Export charts as PNG
- Report generation

### Phase 3 Deliverables
- [ ] Risk metrics (Sortino, Calmar, Beta)
- [ ] Monte Carlo simulations
- [ ] Rolling returns
- [ ] yfinance live data
- [ ] Export options
- [ ] Full dark mode support

---

## Execution Order

```
Phase 1 (Week 1)
├── Day 1-2: Config + Requirements
├── Day 3-4: Data loader + Base strategy
├── Day 5: Metrics utilities
├── Day 6-7: App skeleton + Testing

Phase 2 (Week 2)
├── Day 8-9: Strategy implementations
├── Day 10-11: Plotting utilities
├── Day 12-13: Sidebar + Components
├── Day 14: Testing + Polish

Phase 3 (Week 3)
├── Day 15-16: Risk metrics
├── Day 17-18: Monte Carlo
├── Day 19-20: yfinance + Exports
├── Day 21: Final testing + Documentation
```

---

## Dependencies

| Phase | Depends On |
|-------|-------------|
| 1.3 Base Strategy | 1.2 Data Loader |
| 1.5 Main App | 1.1, 1.2, 1.3, 1.4 |
| 2.1 Strategies | 1.3 Base Strategy |
| 2.2 Plotting | 1.4 Metrics |
| 2.3 Components | 2.1, 2.2 |
| 3.1 Risk Metrics | 1.4 Metrics |
| 3.3 Monte Carlo | 1.4 Metrics |
| 3.4 yfinance | 1.2 Data Loader |

---

## Key Functions Reference

### utils/data_loader.py
```python
def load_csv(filepath: str) -> pd.DataFrame
def validate_data(df: pd.DataFrame) -> bool
def get_data_summary(df: pd.DataFrame) -> dict
def load_yfinance(ticker: str, start: str, end: str) -> pd.DataFrame
```

### strategies/base.py
```python
class BaseStrategy(ABC):
    def generate_signals(self, df, params) -> pd.DataFrame
    def backtest(self, df, params) -> dict
```

### utils/metrics.py
```python
def calculate_total_return(portfolio) -> float
def calculate_cagr(portfolio, years) -> float
def calculate_max_drawdown(portfolio) -> float
def calculate_sharpe(portfolio, risk_free=0.06) -> float
def calculate_win_rate(trades) -> float
```

### utils/plotting.py
```python
def plot_equity_curve(portfolio, benchmark=None, dark=False) -> go.Figure
def plot_drawdown(portfolio, dark=False) -> go.Figure
def plot_monthly_heatmap(returns, dark=False) -> go.Figure
def export_chart(fig, filename) -> bytes
```

### components/sidebar.py
```python
def render_sidebar():
    # Returns: data, strategy, params dict
```

---

## Testing Checklist

- [ ] CSV with various date formats loads
- [ ] All 4 strategies produce results
- [ ] Metrics match manual calculations
- [ ] Charts render in both themes
- [ ] Trade log sorts and filters
- [ ] Export downloads correct data
- [ ] Backtest completes in <5s
- [ ] No errors on empty data

---

## Notes

- Use `@st.cache_data` for expensive operations
- Keep strategy logic separate from UI
- Use dataclasses for config objects
- Handle edge cases gracefully
- Add error messages for invalid input