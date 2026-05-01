# Trading Strategy Dashboard - Design Specification

## Project Overview
- **Project Name**: Trading Strategy Dashboard
- **Type**: Web-based backtesting application (Streamlit)
- **Core Functionality**: Analyze and backtest trading strategies with portfolio tracking, performance metrics, and visualizations
- **Target Users**: Non-technical traders, investors, and enthusiasts

---

## Architecture

### Directory Structure
```
SwpBacktesting/
├── app.py                     # Main Streamlit entry point
├── config.py                  # Configuration and defaults
├── requirements.txt           # Dependencies
├── strategies/
│   ├── __init__.py
│   ├── base.py              # BaseStrategy abstract class
│   ├── momentum.py          # Momentum strategy
│   ├── ath_breakout.py      # All-Time High Breakout
│   ├── moving_average.py    # EMA Crossover strategy
│   └── withdrawal.py        # Portfolio withdrawal strategy
├── utils/
│   ├── __init__.py
│   ├── data_loader.py       # CSV loading + yfinance
│   ├── metrics.py          # Performance metrics
│   ├── plotting.py        # Plotly + Matplotlib charts
│   └── cache.py           # Caching utilities
├── components/
│   ├── __init__.py
│   ├── sidebar.py          # Sidebar inputs
│   ├── tabs.py             # Tab content handlers
│   ├── trade_log.py        # Trade table display
│   └── metrics_display.py # KPI cards
├── data/                    # Data folder
└── docs/                    # Documentation
```

---

## UI/UX Specification

### Layout Structure

**Sidebar (Left Panel - 300px)**
- Data Input Section
  - File uploader (CSV)
  - Preloaded dataset dropdown
  - yfinance ticker input
- Strategy Selection
  - Dropdown selector
  - Strategy rules display (expandable)
- Parameters Section
  - Initial Capital (₹)
  - Stop Loss (%)
  - EMA Period (default: 220)
  - Number of Stocks to Hold
  - Transaction Cost (%)
  - Rebalancing Frequency
- Withdrawal Settings (collapsible)
  - Fixed Amount (₹)
  - Frequency
- Theme Toggle

**Main Area (Tabs)**
1. **Overview Tab**
   - Metrics cards (6 columns)
   - Data summary
2. **Charts Tab**
   - Equity curve
   - Benchmark comparison
   - Drawdown chart
   - Monthly heatmap
3. **Trades Tab**
   - Trade log table
   - Download button
4. **Analytics Tab**
   - Risk metrics
   - Rolling returns
   - Monte Carlo simulation

### Visual Design

**Color Palette**
- Primary: #1f77b4 (Streamlit Blue)
- Success/Profit: #28a745 (Green)
- Loss/Danger: #dc3545 (Red)
- Warning: #ffc107 (Amber)
- Background Light: #ffffff
- Background Dark: #0e1117
- Surface Dark: #1e1e1e
- Text Light: #262730
- Text Dark: #fafafa

**Typography**
- Font: System default (sans-serif)
- Heading Size: 24px (h1), 20px (h2), 16px (h3)
- Body: 14px
- Small: 12px

**Spacing**
- Sidebar padding: 20px
- Card gap: 10px
- Section gap: 30px

**Components**
- Metric Cards: st.metric with delta
- Tables: st.dataframe with sorting
- Charts: Plotly interactive figures
- Buttons: st.button with primary style

---

## Functionality Specification

### 1. Data Input

**CSV Upload**
- Accept single or multiple CSV files
- Required columns: Date, Close (or Adj Close)
- Optional: Open, High, Low, Volume
- Parse dates flexibly
- Show: Date range, record count, missing values

**Preloaded Datasets**
- NIFTYBEES (^NSEBANK)
- HDFC Balanced Advantage (0P0001EI12.BO)
- User can add more to config

**yfinance Integration**
- Ticker input field
- Auto-download on submit
- Cache for performance

### 2. Strategy Selection

| Strategy | Description | Parameters |
|----------|-------------|------------|
| Momentum | Buy top performers by % return over period | Lookback period |
| ATH Breakout | Break above all-time high | Confirmation bars |
| Moving Average | EMA crossover | Fast EMA, Slow EMA |
| Withdrawal | Fixed withdrawal backtest | Amount, Frequency |

**Strategy Rules Display**
- Show description when selected
- Expandable section with logic

### 3. Backtest Engine

**Execution Flow**
1. Load price data
2. Apply strategy signals
3. Simulate trades
4. Track portfolio
5. Calculate metrics

**Parameters**
- Initial Capital: ₹1,00,000 (default)
- Stop Loss: 0% (no stop) to 20%
- EMA Period: 220 (default)
- Max Stocks: 1 to 10
- Transaction Cost: 0% to 1%
- Rebalancing: Daily / Monthly

### 4. Output Metrics

**Core Metrics**
- Total Returns (%)
- CAGR (%)
- Max Drawdown (%)
- Sharpe Ratio
- Number of Trades
- Win Rate (%)
- Final Portfolio Value

**Risk Metrics**
- Sortino Ratio
- Calmar Ratio
- Volatility (Annual)
- Beta (vs benchmark)

**Advanced Metrics**
- Rolling Returns (1Y, 3Y, 5Y)
- Monte Carlo (1000 simulations)
- Scenario Analysis

### 5. Visualizations

| Chart | Library | Interactive |
|-------|---------|-------------|
| Equity Curve | Plotly | Yes |
| Benchmark | Plotly | Yes |
| Drawdown | Plotly | Yes |
| Monthly Heatmap | Plotly | Yes |
| Trade Histogram | Plotly | Yes |
| Monte Carlo | Plotly | Yes |
| Exports | Matplotlib | No |

### 6. Trade Log

**Columns**
- Entry Date
- Exit Date
- Symbol
- Entry Price
- Exit Price
- Return (%)
- Holding Period

**Features**
- Sortable columns
- Filter by date/return
- Download as CSV

### 7. Dark Mode

**Implementation**
- Use Streamlit session state
- Manual toggle in sidebar
- Remember preference
- Apply to all charts

---

## Data Specifications

### Input CSV Format
```csv
Date,Open,High,Low,Close,Volume
2024-01-01,100.0,105.0,99.0,104.0,1000000
```

### Price Data Processing
- Use Adj Close for returns
- Handle missing values (forward fill)
- Resample to required frequency

---

## Implementation Priority

### Phase 1 - Core (Must Have)
1. Streamlit app setup with tabs
2. CSV data upload and display
3. Single strategy backtest
4. Basic metrics display
5. Equity curve chart

### Phase 2 - Features
1. Multiple strategies
2. Trade log table
3. Benchmark comparison
4. Drawdown chart
5. Dark mode toggle

### Phase 3 - Advanced
1. Risk metrics
2. Monthly heatmap
3. Monte Carlo simulation
4. yfinance integration
5. Export functionality

---

## Acceptance Criteria

### Visual Checkpoints
- [ ] Sidebar loads with all input sections
- [ ] Data upload works for CSV files
- [ ] Strategy dropdown shows all 4 strategies
- [ ] Parameter inputs are functional
- [ ] Backtest button triggers execution
- [ ] Metrics display in cards
- [ ] Charts render correctly
- [ ] Trade log shows sortable table
- [ ] Dark mode toggle works
- [ ] Export buttons function

### Functional Checkpoints
- [ ] CSV parsing handles dates correctly
- [ ] Backtest calculates accurate returns
- [ ] Metrics match expected values
- [ ] Charts update with new data
- [ ] Trade log filters work
- [ ] Download produces valid CSV
- [ ] Performance is acceptable (<5s for 1 year)

---

## Notes

- Keep code modular for easy extension
- Use caching for repeat calculations
- Handle errors gracefully with messages
- Focus on UX over features
- Test with sample data first