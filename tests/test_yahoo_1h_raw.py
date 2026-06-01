import yfinance as yf

df = yf.download(
    "EURUSD=X",
    start="2025-01-01",
    end="2025-06-01",
    interval="1h",
    auto_adjust=False,
    progress=False,
)

print(df.head())
print()
print(df.columns)
print()
print(df.index)
print()
print("ROWS =", len(df))
