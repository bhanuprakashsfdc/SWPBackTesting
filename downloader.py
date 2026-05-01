import os
import yfinance as yf
import pandas as pd

# -------- CONFIG --------
TICKER = "0P0001EI12.BO"
OUTPUT_FOLDER = "data"
OUTPUT_FILE = "HDFC_Balanced_Advantage_monthly.csv"

# Ensure folder exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# -------- DOWNLOAD DATA --------
df = yf.download(
    TICKER,
    start="2000-01-01",
    interval="1d",   # download daily first
    progress=False
)

# Flatten the column MultiIndex if present
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

if df.empty:
    raise ValueError("No data downloaded. Check ticker.")

# -------- CONVERT TO MONTHLY --------
monthly_df = df.resample('ME').agg({
    'Open': 'first',
    'High': 'max',
    'Low': 'min',
    'Close': 'last',
    'Volume': 'sum'
})

monthly_df.dropna(inplace=True)

# Reset index for CSV
monthly_df.reset_index(inplace=True)

# -------- SAVE --------
output_path = os.path.join(OUTPUT_FOLDER, OUTPUT_FILE)
monthly_df.to_csv(output_path, index=False)

print(f"✅ Monthly data saved to: {output_path}")